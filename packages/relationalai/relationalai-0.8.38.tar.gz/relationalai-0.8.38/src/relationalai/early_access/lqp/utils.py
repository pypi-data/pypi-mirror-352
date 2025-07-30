from relationalai.early_access.lqp import ir as lqp

class UniqueNames:
    def __init__(self):
        # Track count of seen names
        self.seen = dict[str, int]()
        # Maps id to unique name
        self.id_to_name = dict[int,str]()

    def get_name(self, name: str) -> str:
        # TODO: Do we need to be threadsafe?
        if name in self.seen:
            self.seen[name] += 1
            id = self.seen[name]
            return f"{name}_{id}"
        else:
            self.seen[name] = 1
            return f"{name}"

    # Get a unique name for the given id. If the id is already in the map, return the
    # existing name. Otherwise, generate a new name using the suggested_name and
    # store it in the map.
    def get_name_by_id(self, id: int, suggested_name:str) -> str:
        if id in self.id_to_name:
            return self.id_to_name[id]

        name = self.get_name(suggested_name)
        self.id_to_name[id] = name
        return name

class TranslationCtx:
    def __init__(self, model):
        # TODO: comment these fields
        self.unique_names = UniqueNames()
        self.id_to_orig_name = {}
        self.output_ids = []

def gen_unique_var(ctx: TranslationCtx, name_hint: str):
    """
    Generate a new variable with a unique name based on the provided hint.
    """
    name = ctx.unique_names.get_name(name_hint)
    return lqp.Var(name=name, meta=None)
