"""
    Support for dependency analysis of metamodel IRs.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterable, Optional, Tuple

from relationalai.early_access.metamodel import ir, helpers, visitor
from relationalai.early_access.metamodel.util import FrozenOrderedSet, OrderedSet, ordered_set

@contextmanager
def ctx_frame(ctx: AnalysisContext, task: ir.Logical):
    """
    Create a new frame in this context while analysing this task.

    This can be used by compiler passes when analysing a Logical. This context manager will
    guarantee that a frame is created at start, and it will be exited at the end. Example:

    def handle(self, task: ir.Logical, ctx: AnalysisContext)
        with ctx_frame(ctx, task) as frame:
            ... process logical using frame
    """
    frame = ctx.new_frame(task)
    try:
        yield frame
    finally:
        ctx.exit_frame()

class Frame():
    """
    Dependency analysis information from the perspective of a Logical.

    The frame contains, for each sub-task of a logical, the set of variables that this
    sub-task requires as input and provides as output.
    """
    def __init__(self, bindings: VarBindingAnalysis, logical: ir.Logical, parent_frame: Optional[Frame]):
        self._bindings = bindings
        self._logical = logical
        self._parent_frame = parent_frame
        # for each child task, the siblings it depends on
        self._dependencies: dict[ir.Task, OrderedSet[ir.Task]] = self._compute_dependencies()
        self._replacements: dict[ir.Task, ir.Task] = dict()

    def task_inputs(self, task: ir.Task) -> OrderedSet[ir.Var]:
        """ Return the set of variables this sub-task requires as input. """
        return self._bindings.get_inputs(task)

    def task_outputs(self, task: ir.Task):
        """ Return the set of variables this sub-task provides as output. """
        return self._bindings.get_outputs(task)

    def task_dependencies(self, task: ir.Task) -> OrderedSet[ir.Task]:
        """
        Return the siblings that this sub-task depends on.

        Intuitively, a task depends on all siblings that impacts it via dataflow. Given a
        task, the dependencies are siblings that:

        1. have an output in common (this means the tasks join on the same variable), or
        2. have an output that this task has an input (this means this task depends as input
        on the output of the other task), or
        3. are in the transitive closure of the dependencies above.

        Furthermore, for nested Logicals we additionally compute an expanded scope by
        bringing siblings that depend on it (i.e. the inverse of the relation above). These
        are siblings that would need to be extracted together with the Logical to make the
        extracted rule correct.

        For example, in this Logical, we compute the following input/output bindings:

        Logical
            Person(p)         (out: p)
            Logical [n=None]  (in: p, out: n)
                name(p, n)        (out: p, n)
            age(p, a)         (out: p, a)
            x = a + 1         (in: a, out: x)
            x > 10            (in: x)
            output(n, x)      (in: n, x)


        Then, we compute the following dependencies (which would be returned by this method):

        Dependencies:
            Person  -> age (join p)
            Logical -> Person, age (io p), x=, x> (scope)
            age     -> Person (join p)
            x=      -> age (io a), Person (transitive)
            x>      -> x= (io x), age, Person (transitive)
            output  -> Logical (io n), x= (io x), x>, age, Person (transitive)

        Note that the nested Logical also depends on x= and x>, because if we decided to
        make a rule with that Logical we would need those lookups to hold on the extracted
        rule.
        """
        result = ordered_set()
        if task in self._dependencies:
            for dep in self._dependencies[task]:
                result.add(self._replacements.get(dep, dep))
        return result

    def replaced(self, original: ir.Task, replacement: ir.Task):
        """
        Inform the frame that, during some pass, this original task was replaced with this
        replacement task. This affects the result of .task_dependencies(...) since the frame
        will answer with the replacement when the original is in the set of dependencies.
        """
        self._replacements[original] = replacement

    def intersection(self, tasks: OrderedSet[ir.Task]) -> Tuple[OrderedSet[ir.Task], OrderedSet[ir.Var]]:
        """
        Intersect the task dependencies and input bindings for all these tasks.
        """
        # start with dependencies from an arbitrary task, cloning to ensure we do not modify
        # the incoming ordered sets
        sample = tasks.some()
        deps = self.task_dependencies(sample)
        if deps is None:
            return ordered_set(), ordered_set()
        deps = OrderedSet.from_iterable(deps)
        vars = OrderedSet.from_iterable(self._bindings.get_inputs(sample))

        # now extract from the original sets
        for t in tasks:
            if t == sample:
                continue

            # compute sibling dependencies
            for dep in deps:
                if dep not in self.task_dependencies(t):
                    deps.remove(dep)
            # compute common input vars
            for v in self._bindings.get_inputs(t):
                if v not in vars:
                    vars.remove(v)
        return deps, vars


    def _compute_dependencies(self) -> dict[ir.Task, OrderedSet[ir.Task]]:
        # flag to indicate that this task has a child that is a logical
        has_nested_logical = False

        # compute direct dependencies between tasks
        task_deps: dict[ir.Task, OrderedSet[ir.Task]] = dict()
        logical_inputs = self._bindings.get_inputs(self._logical)
        for child in self._logical.body:
            if isinstance(child, ir.Logical):
                has_nested_logical = True

            child_deps = ordered_set()
            child_inputs = self._bindings.get_inputs(child)
            child_outputs = self._bindings.get_outputs(child)

            # if the child needs as input something that the logical needs as input, bring the logical dependencies
            if self._parent_frame and logical_inputs & child_inputs:
                child_deps.update(self._parent_frame.task_dependencies(self._logical))

            for sibling in self._logical.body:
                if child is not sibling:
                    # child depends on sibling if:
                    #  1. there is an out in common (they join the same var), or
                    #  2. there is an input in child that is output by sibling
                    sibling_outputs = self._bindings.get_outputs(sibling)
                    if (sibling_outputs & child_outputs or sibling_outputs & child_inputs):
                        child_deps.add(sibling)
            task_deps[child] = child_deps

        # compute transitive closure of dependencies
        for child in self._logical.body:
            # iterative transitive closure accumulating in child_deps
            # TODO: implement a reusable transitive closure function and ensure it performs well
            child_deps = task_deps[child]
            to_visit = ordered_set()
            to_visit.update(child_deps)
            visited = set()
            while(to_visit):
                x = to_visit.pop()
                visited.add(x)
                if x in task_deps:
                    for dep in task_deps[x]:
                        if dep is not child:
                            child_deps.add(dep)
                            if dep not in visited:
                                to_visit.add(dep)

        # only expand scope if there is a nested logical
        if has_nested_logical:
            # compute the inverse of task_deps, making it bidirectional, to be used in the next step
            bidirectional_deps: dict[ir.Task, OrderedSet[ir.Task]] = dict()
            for child, child_deps in task_deps.items():
                bidirectional_deps[child] = OrderedSet.from_iterable(child_deps)
                for child_dep in child_deps:
                    if child_dep not in bidirectional_deps:
                        bidirectional_deps[child_dep] = ordered_set()
                    bidirectional_deps[child_dep].add(child)

            # compute scope (only needed for logicals)
            for child in self._logical.body:
                if not isinstance(child, ir.Logical):
                    continue
                child_deps = task_deps[child]
                to_visit = ordered_set()
                to_visit.update(child_deps)
                visited = set()
                while(to_visit):
                    x = to_visit.pop()
                    visited.add(x)
                    if x in bidirectional_deps and isinstance(x, helpers.BINDERS):
                        for dep in bidirectional_deps[x]:
                            if dep is not child and isinstance(dep, helpers.BINDERS) and dep not in visited and (dep not in task_deps or child not in task_deps[dep]):
                                child_deps.add(dep)
                                to_visit.add(dep)

        # another transitive closure to get the dependency for the binders added above
        # TODO: this fixes the 2-hop problem only, we need to iterate until fixpoint
        for child in self._logical.body:
            child_deps = task_deps[child]
            to_visit = ordered_set()
            to_visit.update(child_deps)
            visited = set()
            while(to_visit):
                x = to_visit.pop()
                visited.add(x)
                if x in task_deps:
                    for dep in task_deps[x]:
                        if dep is not child:
                            child_deps.add(dep)
                            if dep not in visited:
                                to_visit.add(dep)
        return task_deps

class AnalysisContext():
    """
    Maintain global context for passes that use dependency analysis.
    """

    def __init__(self, root: ir.Task):
        # result of varibale binding analysis
        self.bindings = VarBindingAnalysis()
        # the logicals that will be at the top level at the end of the rewrite
        self.top_level: list[ir.Logical] = []
        # new relations created during the pass
        self.relations: list[ir.Relation] = []
        # the stack of frames
        self.frames: list[Frame] = []

        root.accept(self.bindings)

    def new_frame(self, task: ir.Logical) -> Frame:
        """
        Create a new frame to analyze this logical.

        This will create a new Frame, which already analyzes the task, computing dependencies
        between its children, will push this frame into a stack, making it the "current"
        frame, and will return the frame.
        """
        frame = Frame(self.bindings, task, self._peek())
        self.frames.append(frame)
        return frame

    def exit_frame(self):
        """ Remove the current frame from the stack. """
        self.frames.pop()

    def current_frame(self):
        """ Get the current frame or raise exception. """
        if self.frames:
            return self.frames[-1]
        raise Exception("Trying to get a frame from context. This is probably a bug, please report.")

    def _peek(self):
        """ Get the current frame or None. """
        if self.frames:
            return self.frames[-1]
        return None


@dataclass
class VarBindingAnalysis(visitor.Visitor):
    """
    Compute which variables are grounded, and used as input or output for a given task.
    """
    # vars required by the task to be provided from elsewhere
    _input_bindings: dict[ir.Task, OrderedSet[ir.Var]] = field(default_factory=dict)
    # vars provided by the task to other tasks
    _output_bindings: dict[ir.Task, OrderedSet[ir.Var]] = field(default_factory=dict)
    # a stack of variables grounded by the last logical being visited
    _grounded: list[FrozenOrderedSet[ir.Var]] = field(default_factory=list)

    def get_outputs(self, node: ir.Task) -> OrderedSet[ir.Var]:
        if node in self._output_bindings:
            return self._output_bindings[node]
        else:
            return ordered_set()

    def get_inputs(self, node: ir.Task) -> OrderedSet[ir.Var]:
        if node in self._input_bindings:
            return self._input_bindings[node]
        else:
            return ordered_set()

    def _register(self, map, key, val):
        """ Register key -> val in this map, assuming the map holds ordered sets of vals. """
        if val is None or (isinstance(val, Iterable) and not val):
            return
        if key not in map:
            map[key] = ordered_set()
        if isinstance(val, Iterable):
            for v in val:
                map[key].add(v)
        else:
            map[key].add(val)

    #
    # Composite tasks
    #
    def visit_logical(self, node: ir.Logical, parent: Optional[ir.Node]):

        # compute variables grounded by children of this logical
        grounds = ordered_set()
        grounded_by_ancestors = None
        if self._grounded:
            # grounded variables inherited from ancestors
            grounded_by_ancestors = self._grounded[-1]
            grounds.update(grounded_by_ancestors)
        for child in node.body:
            # leaf constructs that ground variables
            if isinstance(child, ir.Lookup):
                for idx, f in enumerate(child.relation.fields):
                    arg = child.args[idx]
                    if not f.input and isinstance(arg, ir.Var):
                        grounds.add(arg)
            elif isinstance(child, ir.Data):
                grounds.update(child.vars)
            elif isinstance(child, ir.Aggregate):
                # register variables depending on the input flag of the aggregation relation
                for idx, f in enumerate(child.aggregation.fields):
                    arg = child.args[idx]
                    if not f.input and isinstance(arg, ir.Var):
                        grounds.add(arg)
            elif isinstance(child, ir.Rank):
                grounds.add(child.result)
            elif isinstance(child, ir.Construct):
                grounds.add(child.id_var)

        # now visit the children
        self._grounded.append(grounds.frozen())
        super().visit_logical(node, parent)
        self._grounded.pop()

        if grounded_by_ancestors:
            # inputs to this logical: grounded y ancestor while being used by a child
            vars = helpers.collect_vars(node)
            self._register(self._input_bindings, node, grounded_by_ancestors & vars)
        # outputs are vars declared as hoisted
        self._register(self._output_bindings, node, helpers.hoisted_vars(node.hoisted))


    def visit_union(self, node: ir.Union, parent: Optional[ir.Node]):
        # visit children first
        super().visit_union(node, parent)

        # inputs taken from all children
        for child in node.tasks:
            self._register(self._input_bindings, node, self._input_bindings.get(child, None))
        # outputs are vars declared as hoisted
        self._register(self._output_bindings, node, helpers.hoisted_vars(node.hoisted))

    def visit_match(self, node: ir.Match, parent: Optional[ir.Node]):
        # visit children first
        super().visit_match(node, parent)

        # inputs taken from all children
        for child in node.tasks:
            self._register(self._input_bindings, node, self._input_bindings.get(child, None))
        # outputs are vars declared as hoisted
        self._register(self._output_bindings, node, helpers.hoisted_vars(node.hoisted))

    def visit_require(self, node: ir.Require, parent: Optional[ir.Node]):
        # visit children first
        super().visit_require(node, parent)

        # TODO: do we need to pull check error task deps?
        # inputs taken from the domain and all check tasks
        self._register(self._input_bindings, node, self._input_bindings.get(node.domain, None))
        for check in node.checks:
            self._register(self._input_bindings, node, self._input_bindings.get(check.check, None))


    #
    # Logical tasks
    #
    def visit_not(self, node: ir.Not, parent: Optional[ir.Node]):

        # visit children first
        super().visit_not(node, parent)

        # not gets the inputs from its child
        self._register(self._input_bindings, node, self._input_bindings.get(node.task, None))

    def visit_exists(self, node: ir.Exists, parent: Optional[ir.Node]):

        # visit children first
        super().visit_exists(node, parent)

        # exists variables are local, so they are ignored

        # the input variables to the exists task becomes outputs of the exists, because we
        # want to join those variables outside (the exists is checking that the inner task
        # holds when joined with those variables)
        if node.task in self._input_bindings:
            for v in self._input_bindings[node.task]:
                self._register(self._output_bindings, node, v)

    #
    # Leaf tasks
    #
    def visit_data(self, node: ir.Data, parent: Optional[ir.Node]):
        # data outputs all its variables
        for v in helpers.vars(node.vars):
            self._register(self._output_bindings, node, v)

        return super().visit_data(node, parent)

    def visit_update(self, node: ir.Update, parent: Optional[ir.Node]):

        # register variables being used as arguments to the update, it's always considered an input
        for v in helpers.vars(node.args):
            self._register(self._input_bindings, node, v)
        return super().visit_update(node, parent)

    def visit_lookup(self, node: ir.Lookup, parent: Optional[ir.Node]):

        # register variables depending on the input flag of the relation bound to the lookup
        for idx, f in enumerate(node.relation.fields):
            if isinstance(node.args[idx], ir.Var):
                if f.input:
                    self._register(self._input_bindings, node, node.args[idx])
                else:
                    self._register(self._output_bindings, node, node.args[idx])
        return super().visit_lookup(node, parent)

    def visit_output(self, node: ir.Output, parent: Optional[ir.Node]):

            # register variables being output, it's always considered an input
        for v in helpers.output_vars(node.aliases):
            self._register(self._input_bindings, node, v)
        return super().visit_output(node, parent)

    def visit_construct(self, node: ir.Construct, parent: Optional[ir.Node]):

        # values are inputs, id_var is an output
        for v in helpers.vars(node.values):
            self._register(self._input_bindings, node, v)
        self._register(self._output_bindings, node, node.id_var)

    def visit_aggregate(self, node: ir.Aggregate, parent: Optional[ir.Node]):

        # register projection and group as inputs
        for v in node.projection:
            self._register(self._input_bindings, node, v)
        for v in node.group:
            self._register(self._input_bindings, node, v)

        # register variables depending on the input flag of the aggregation relation
        for idx, f in enumerate(node.aggregation.fields):
            arg = node.args[idx]
            if isinstance(arg, ir.Var):
                if f.input:
                    self._register(self._input_bindings, node, arg)
                else:
                    self._register(self._output_bindings, node, arg)
        return super().visit_aggregate(node, parent)

    def visit_rank(self, node: ir.Rank, parent: Optional[ir.Node]):

        # register projection and group as inputs
        for v in node.projection:
            self._register(self._input_bindings, node, v)
        for v in node.group:
            self._register(self._input_bindings, node, v)
        for v in node.args:
            self._register(self._input_bindings, node, v)

        self._register(self._output_bindings, node, node.result)
        return super().visit_rank(node, parent)
