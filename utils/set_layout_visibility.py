def set_layout_children_hidden(layout, is_hidden):
    i = layout.count() - 1

    while i >= 0:
        widget = layout.itemAt(i).widget()
        nested_layout = layout.itemAt(i).layout()

        # skip manually hidden widgets
        if widget:
            if not widget.property("is_hidden_manually") and not widget.property(
                "is_always_shown"
            ):
                widget.setHidden(is_hidden)
        elif nested_layout:
            # it's layout
            if not nested_layout.property(
                "is_hidden_manually"
            ) and not nested_layout.property("is_always_shown"):
                set_layout_children_hidden(nested_layout, is_hidden)

        i -= 1


def hide_layout(layout):
    set_layout_children_hidden(layout, True)


def show_layout(layout):
    set_layout_children_hidden(layout, False)
