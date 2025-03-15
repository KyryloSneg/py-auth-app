def set_layout_children_hidden(layout, is_hidden):
  i = layout.count() - 1
  
  while i >= 0:
      widget = layout.itemAt(i).widget()
      widget.setHidden(is_hidden)
      i -= 1
  
  
def hide_layout(layout):
  set_layout_children_hidden(layout, True)
  
  
def show_layout(layout):
  set_layout_children_hidden(layout, False)
