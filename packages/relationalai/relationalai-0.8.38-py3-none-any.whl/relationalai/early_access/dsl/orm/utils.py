import re

from relationalai.early_access.dsl.constants import VERBAL_PART_CONNECTION
from relationalai.early_access.dsl.core.utils import camel_to_snake, to_rai_way_string


# Re-adjusted code from dsl/utils.py - that version was used in the dsl
def build_relation_name_from_reading(reading):
    roles = re.findall(r'\{([^}]+)}', reading)
    text_without_concepts = re.sub(r'\{[^}]+}', '|', reading)
    verbal_parts = [text.strip() for text in text_without_concepts.split('|') if text.strip()]

    for rl, vp in zip(roles, verbal_parts):
        # Prefix
        if vp.endswith("-"):
            i = roles.index(rl)
            verbal_parts[i] = vp.replace("-", "-" + camel_to_snake(roles[i + 1]))
        # Postfix
        if vp.startswith("-"):
            i = roles.index(rl)
            postfix = vp.split(" ")[0]
            if verbal_parts[i] == postfix:
                verbal_parts.remove(vp)
            else:
                verbal_parts[i] = vp.replace(postfix, "")

    rel_name = ""
    if len(roles) == 1:
        if len(verbal_parts) > 0:
            rel_name = to_rai_way_string(verbal_parts[0])
        if not rel_name:
            rel_name = camel_to_snake(roles[0])
    elif len(roles) == 2:
        s_role = roles[1]
        if len(verbal_parts) > 0:
            rel_name = to_rai_way_string(verbal_parts[0])
            if verbal_parts[0].strip().startswith(("has", "is")):
                if not rel_name:
                    rel_name += camel_to_snake(s_role)
        else:
            rel_name = camel_to_snake(s_role)
    else:
        join_parts = [to_rai_way_string(verbal_parts[0], False)]
        for i in range(1, len(roles)):
            role = roles[i]
            if not join_parts[len(join_parts) - 1].endswith(camel_to_snake(role)):
                join_parts.append(to_rai_way_string(role.split(":")[0])) # take a role name instead of type if any
            if i < len(roles) - 1:
                join_parts.append(to_rai_way_string(verbal_parts[i]))
        rel_name = VERBAL_PART_CONNECTION.join(join_parts)
    return rel_name
