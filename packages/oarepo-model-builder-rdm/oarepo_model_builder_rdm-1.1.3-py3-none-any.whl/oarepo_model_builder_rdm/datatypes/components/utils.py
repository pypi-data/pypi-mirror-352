def replace_base_class(
    container: dict,
    original_base_class: str,
    replacement_base_class: str,
    set_if_empty: bool = True,
) -> None:
    base_classes = container.setdefault("base-classes", [])
    if base_classes:
        if original_base_class in base_classes:
            idx = base_classes.index(original_base_class)
            base_classes[idx] = replacement_base_class
    elif set_if_empty:
        base_classes.append(replacement_base_class)
