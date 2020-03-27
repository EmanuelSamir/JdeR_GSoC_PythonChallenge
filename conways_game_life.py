#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import json


def conv_2d(X, window):
	# X: array
	# window: 3x3 array 
	rows_X, cols_X  = np.shape(X)

	conv_array = np.zeros([rows_X, cols_X ] )

	for i in range(cols_X - 3):
		for j in range(rows_X - 3):
			conv_array[j+1,i+1] = np.sum(X[j:j+3,i:i+3] * window)
	return conv_array

def generation_update(old_generation):
	# Padding with dead cells
	old_generation_padded = np.pad(old_generation,((1, 1), (1, 1)), 'constant', constant_values=((0, 0),(0, 0)))

	# Generate Scoring Grid through convolution
	window = np.array([[1,1,1],[1,0,1],[1,1,1]])
	scoring_grid_padded = conv_2d(old_generation_padded, window)

	scoring_grid = scoring_grid_padded[1:-1,1:-1]

	# Update cell - Next generation
	## old_generation = dead and it has 3 live neighbors, reproduction
	## old_generation = live and does not have less than 2 (underpopulation) or more than 3 (overpopulation), live
	## Other cases, die
	next_generation = (old_generation == 0) * (scoring_grid == 3)  + (old_generation == 1) * (scoring_grid == 3)  + (old_generation == 1) * (scoring_grid == 2)

	return next_generation

class Grid:
	def __init__(self, rows, cols, grid_initial):
		self.rows = rows
		self.cols = cols

		self.grid = self.grid_initialization(grid_initial)

	def grid_initialization(self, grid_initial):
		if grid_initial == "zeros":
			grid = np.zeros(shape=(self.rows, self.cols), dtype = np.bool)
		elif grid_initial == "ones":
			grid = np.ones(shape=(self.rows, self.cols), dtype = np.bool)
		elif grid_initial == "random":
			grid = np.random.randint(2, size=(self.rows, self.cols), dtype = np.bool)
		else:
			grid = np.random.randint(2, size=(self.rows, self.cols), dtype = np.bool)

		return grid


class GridGUI:
	def __init__(self, data):
		self.height_in = data["height_inches"]
		self.width_in = data["width_inches"]

		self.rows = data["rows"]
		self.cols = data["cols"]

		self.grid_initial = data["grid_initialization"]

		self.grid = Grid(self.rows, self.cols, self.grid_initial)

		self.start_on = False

		self.f = plt.figure(figsize = (self.width_in,self.height_in))
		self.ax = self.f.add_subplot(111)
		self.ax.xaxis.set_visible(False)
		self.ax.yaxis.set_visible(False)
		plt.subplots_adjust(bottom=0.2)

		self.grid_image = self.ax.imshow(self.grid.grid, cmap='gray', vmin = 0, vmax = 1)

		pixelpicking = PixelPicking(self.grid_image, self.ax, self.grid)

		axbutton = plt.axes([0.7, 0.05, 0.1, 0.075])
		self.button = Button(axbutton, 'Start')
		self.button.on_clicked(self.button_pressed)

		plt.ion()
		
		try:
			while 1:
				plt.pause(0.5)
				if self.start_on:
					self.grid.grid = generation_update(self.grid.grid)
				self.grid_image.set_data(self.grid.grid)
				self.grid_image.figure.canvas.draw()
		except:
			pass

	def button_pressed(self, event):
		if self.start_on:
			self.button.label.set_text('Start')
			self.start_on = False
		else:
			self.button.label.set_text('Stop')
			self.start_on = True
		self.grid_image.figure.canvas.draw()


class PixelPicking:
	def __init__(self, image, ax, grid):
		self.image = image
		self.grid = grid
		self.ax = ax

		self.cidmouse = image.figure.canvas.mpl_connect('button_press_event', self.mousepressCall)

	def mousepressCall(self, event):
		xs,ys = event.xdata, event.ydata
		if xs is not None and ys is not None:
			col_clicked, row_clicked = np.round(xs).astype(int), np.round(ys).astype(int)
			self.grid.grid[row_clicked, col_clicked] = int(self.grid.grid[row_clicked, col_clicked] == 0)
			self.image.set_data(self.grid.grid)
			self.image.figure.canvas.draw()

def main():
	# Read file JSON
	with open('./config.json') as f:
		data = json.load(f)
	## One option is to define game size
	app = GridGUI(data)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass