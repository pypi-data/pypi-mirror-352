import sdypy as sd
import meshio
import numpy as np

mesh = meshio.read("L_bracket.msh")

# extract nodes and elements from mesh
nodes = mesh.points
elements = []
for cells in mesh.cells:
    if cells.type == "quad":
        elements.append(cells.data)
elements = np.vstack(elements)


mode_shape = np.zeros((nodes.shape[0], 3))
mode_shape[:, 0] = 10.0

plotter = sd.view.Plotter3D()
plotter.add_fem_mesh(nodes, elements, animate=mode_shape, field="norm")
plotter.show(show_grid=True, show_axes=True)


