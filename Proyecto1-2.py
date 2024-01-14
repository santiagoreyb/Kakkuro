import tkinter as tk
import random
from tkinter import ttk
import tkinter.messagebox
from queue import PriorityQueue
import random
import heapq
import itertools

class KakkuroGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Kakkuro Game")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        frame = tk.Frame(root)
        frame.pack(expand=True, fill="both")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self.size_label = tk.Label(frame, text="Selecciona el tamaño de la matriz:")
        self.size_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        self.size_var = tk.StringVar()
        self.size_combobox = ttk.Combobox(frame, textvariable=self.size_var,
                                          values=["3", "4", "5"])
        self.size_combobox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.play_button = tk.Button(frame, text="Iniciar Juego", command=self.show_game_window)
        self.play_button.grid(row=2, column=0, columnspan=2, padx=10, pady=15)

    def show_game_window(self):
        selected_size = self.size_var.get()

        if selected_size:
            size = int(selected_size)
            filename = f"{size}.txt"

            matrices = self.read_matrices(size, size)

            random_id = random.choice(list(matrices.keys()))
            random_matrix = matrices[random_id]

            game_window = tk.Toplevel(self.root)
            game_window.title("Tablero Kakkuro")

            entry_frame = tk.Frame(game_window)
            entry_frame.pack()

            entry_matrix = []
            for i in range(size):
                row_entries = []
                for j in range(size):
                    cell_value = random_matrix[i][j]
                    if cell_value == "0":
                        entry = tk.Entry(entry_frame, width=4)
                        entry.insert(0, "")
                        entry.grid(row=i, column=j, padx=5, pady=5)
                        entry.config(validate="key", validatecommand=(self.root.register(self.validate_entry), "%P"))
                        row_entries.append(entry)
                    elif cell_value == "-1\\-1":
                        label = tk.Label(entry_frame, text="", width=4, height=2, relief="solid")
                        label.grid(row=i, column=j, padx=5, pady=5)
                        row_entries.append(None)
                    elif '\\' in cell_value:
                        label = tk.Label(entry_frame, text=cell_value.replace('-1', ''), width=4, height=2, relief="solid")
                        label.grid(row=i, column=j, padx=5, pady=5)
                        row_entries.append(None)
                entry_matrix.append(row_entries)

            submit_button = tk.Button(entry_frame, text="Verificar Tablero", command=lambda: self.validate_board(entry_matrix, random_matrix))
            submit_button.grid(row=size, columnspan=size, padx=10, pady=15)

            solve_button = tk.Button(entry_frame, text="Solucionar Tablero", command=lambda: self.solve_board(random_matrix))
            solve_button.grid(row=size + 1, columnspan=size, padx=10, pady=15)
        else:
            tk.messagebox.showwarning("Advertencia", "Por favor, selecciona un tamaño de matriz.")
            
    def read_matrices(self, cf, cc):
        matrices = {}
        current_matrix_id = None
        x = False  # Inicializar x como False

        with open("matrices.txt", "r") as file:
            lines = file.readlines()

        idm = 0
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) == 2:
                    if int(parts[0]) == cf:
                        current_matrix_id = idm
                        idm += 1
                        matrices[current_matrix_id] = []
                        x = True  # Establecer x como True si hay coincidencia con cf
                    else:
                        x = False  # Establecer x como False si no hay coincidencia con cf
                else:
                    if x:  # Verificar si x es True
                        row, col, n, m = map(int, parts)
                        if n == -1 and m == -1:
                            value = "-1\\-1"
                        elif n == -1:
                            value = f"-1\\{m}"
                        elif m == -1:
                            value = f"{n}\\-1"
                        else:
                            value = f"{n}\\{m}"
                        matrices[current_matrix_id].append((row, col, value))

        # Create the final matrix for each identifier
        for matrix_id, cell_values in matrices.items():
            max_row = max(cell[0] for cell in cell_values)
            max_col = max(cell[1] for cell in cell_values)
            current_matrix = [['0' for _ in range(max_col + 1)] for _ in range(max_row + 1)]
            for row, col, value in cell_values:
                current_matrix[row][col] = value
            matrices[matrix_id] = current_matrix

        return matrices


    def validate_board(self, entry_matrix, random_matrix):
        if entry_matrix:
            board = [[entry.get() if entry else None for entry in row] for row in entry_matrix]
            if self.is_valid_kakkuro(board, random_matrix):
                tk.messagebox.showinfo("Resultado", "¡El tablero Kakkuro es válido!")
            else:
                tk.messagebox.showerror("Resultado", "El tablero Kakkuro no es válido.")

    def is_valid_kakkuro(self, board, random_matrix):
        for i in range(len(board)):
            for j in range(len(board[i])):
                cell_value = random_matrix[i][j]
                if cell_value is not None and '\\' in cell_value:
                    parts = cell_value.split('\\')
                    n = int(parts[0]) if parts[0].isdigit() else None
                    m = int(parts[1]) if parts[1].isdigit() else None
                    
                    # Verificar suma hacia abajo
                    if n is not None and not self.validate_sum_down(board, i, j, n, random_matrix):
                        return False
                    
                    # Verificar suma hacia la derecha
                    if m is not None and not self.validate_sum_right(board, i, j, m, random_matrix):
                        return False
        return True

    def validate_sum_down(self, board, row, col, n, random_matrix):
        # Validar suma hacia abajo
        current_sum = 0
        seen_values = set()
        for i in range(row + 1, len(board)):
            cell_value = board[i][col]
            cell_value2 = random_matrix[i][col]
            if cell_value is not None and cell_value.isdigit():
                value = int(cell_value)
                if value in seen_values:
                    tk.messagebox.showerror("Error", "Valores repetidos en la misma fila o columna.")
                    return False
                current_sum += value
                seen_values.add(value)
            elif cell_value2 is not None and ('\\' in cell_value2 or '-1\\-1' in cell_value2):
                break
            else:
                return False
        return current_sum == n

    def validate_sum_right(self, board, row, col, m, random_matrix):
        # Validar suma hacia la derecha
        current_sum = 0
        seen_values = set()
        for j in range(col + 1, len(board[row])):
            cell_value = board[row][j]
            cell_value2 = random_matrix[row][j]
            if cell_value is not None and cell_value.isdigit():
                value = int(cell_value)
                if value in seen_values:
                    tk.messagebox.showerror("Error", "Valores repetidos en la misma fila o columna.")
                    return False
                current_sum += value
                seen_values.add(value)
            elif cell_value2 is not None and ('\\' in cell_value2 or '-1\\-1' in cell_value2):
                break
            else:
                return False
        return current_sum == m

    def validate_entry(self, new_value):
        if new_value == "":
            return True
        try:
            value = int(new_value)
            return 1 <= value <= 9
        except ValueError:
            return False
        
    def solve_board(self, random_matrix):
        empty_cells = []  # Almacenar las coordenadas de las celdas vacías
        for i in range(len(random_matrix)):
            for j in range(len(random_matrix[i])):
                if random_matrix[i][j] == '0':
                    empty_cells.append((i, j))
        print(random_matrix)
        solver = KakkuroSolver(random_matrix)
        solution = solver.solve_kakkuro()
        if solution:
            print(solution)
            solved_board = [['' if cell is None else str(cell) for cell in row] for row in solution]
            self.show_solution(solved_board)
        else:
            tk.messagebox.showinfo("Solución", "No se pudo encontrar una solución válida.")


    def show_solution(self, solution):
        print(solution)
        solution_window = tk.Toplevel(self.root)
        solution_window.title("Solución del Tablero Kakkuro")

        solution_frame = tk.Frame(solution_window)
        solution_frame.pack()

        for i, row in enumerate(solution):
            for j, value in enumerate(row):
                if value == '-1\\-1':
                    label = tk.Label(solution_frame, text="", width=4, height=2, relief="solid")
                else:
                    cell_value = value.replace('-1', '').replace('\\-1', '\\') if '-1' in value else value
                    label = tk.Label(solution_frame, text=cell_value, width=4, height=2, relief="solid")
                label.grid(row=i, column=j, padx=5, pady=5)


class KakkuroSolver:
    
    def __init__(self, random_matrix):
        self.random_matrix = random_matrix
        
    def is_valid_kakkuro(self, board, random_matrix):
        for i in range(len(board)):
            for j in range(len(board[i])):
                cell_value = random_matrix[i][j]
                if cell_value is not None and '\\' in cell_value:
                    parts = cell_value.split('\\')
                    n = int(parts[0]) if parts[0].isdigit() else None
                    m = int(parts[1]) if parts[1].isdigit() else None
                    
                    # Verificar suma hacia abajo
                    if n is not None and not self.validate_sum_down(board, i, j, n, random_matrix):
                        return False
                    
                    # Verificar suma hacia la derecha
                    if m is not None and not self.validate_sum_right(board, i, j, m, random_matrix):
                        return False
        return True

    def validate_sum_down(self, board, row, col, n, random_matrix):
        # Validar suma hacia abajo
        current_sum = 0
        seen_values = set()
        for i in range(row + 1, len(board)):
            cell_value = board[i][col]
            cell_value2 = random_matrix[i][col]
            if cell_value is not None and cell_value.isdigit():
                value = int(cell_value)
                if value in seen_values:
                    return False
                current_sum += value
                seen_values.add(value)
            elif cell_value2 is not None and ('\\' in cell_value2 or '-1\\-1' in cell_value2):
                break
            else:
                return False
        return current_sum == n

    def validate_sum_right(self, board, row, col, m, random_matrix):
        # Validar suma hacia la derecha
        current_sum = 0
        seen_values = set()
        for j in range(col + 1, len(board[row])):
            cell_value = board[row][j]
            cell_value2 = random_matrix[row][j]
            if cell_value is not None and cell_value.isdigit():
                value = int(cell_value)
                if value in seen_values:
                    return False
                current_sum += value
                seen_values.add(value)
            elif cell_value2 is not None and ('\\' in cell_value2 or '-1\\-1' in cell_value2):
                break
            else:
                return False
        return current_sum == m
    '''
    def solve_kakkuro(self):
        empty_cells = []  # Almacenar las coordenadas de las celdas vacías
        for i in range(len(self.random_matrix)):
            for j in range(len(self.random_matrix[i])):
                if self.random_matrix[i][j] == '0':
                    empty_cells.append((i, j))

        found_solution = False
        # Probar cada combinación de números en las celdas vacías hasta encontrar una solución válida
        for combination in itertools.product(range(1, 10), repeat=len(empty_cells)):
            temp_matrix = [row[:] for row in self.random_matrix]  # Crear una copia temporal del tablero
            for index, (row, col) in enumerate(empty_cells):
                temp_matrix[row][col] = str(combination[index])  # Probar cada combinación de números en el tablero
            if self.is_valid_kakkuro(temp_matrix, self.random_matrix):  # Verificar si la combinación es válida
                found_solution = True
                return temp_matrix  # Devolver la solución encontrada

        return None  # Devolver None si no se encontró una solución válida
    '''
    def get_cell_value(self, row, col):
       
        # Comprobar si la celda está fuera de los límites
        if row < 0 or row >= len(self.random_matrix) or col < 0 or col >= len(self.random_matrix[row]):
            return None
        # Comprobar si la celda está vacía
        elif self.random_matrix[row][col] != '0':
            return self.random_matrix[row][col]
        else:
            return None
        
    def get_cell_options(self, empty_cells):
         # Calcular el número de opciones posibles para cada celda vacía
        cell_options = {cell: list(range(1, 10)) for cell in empty_cells}
        
        for cell in cell_options:
            value_one_solution = False
            row, col = cell
            #-----------------UNA SOLUCION-----------------
            # FILAS
            # no es un valor en los bordes
            if col > 0 and col < len(self.random_matrix[row]) - 1:
                row_left_value = self.get_cell_value(row, col-1)
                row_right_value = self.get_cell_value(row, col+1)
                if row_left_value is not None and row_right_value is not None:
                    value = row_left_value.split('\\')
                    cell_options[cell] = [int(value[1])]
                    value_one_solution = True

            # es un valor en el borde derecho
            elif col == len(self.random_matrix[row]) - 1:
                row_left_value = self.get_cell_value(row, col-1)
                if row_left_value is not None:
                    value = row_left_value.split('\\')
                    cell_options[cell] = [int(value[1])]
                    value_one_solution = True
            
            #COLUMNAS
            # no es un valor en los bordes
            if row > 0 and row < len(self.random_matrix) - 1:
                col_up_value = self.get_cell_value(row-1, col)
                col_down_value = self.get_cell_value(row+1, col)
                if col_up_value is not None and col_down_value is not None:
                    value = col_up_value.split('\\')
                    cell_options[cell] = [int(value[0])]
                    value_one_solution = True

            # es un valor en el borde inferior
            elif row == len(self.random_matrix) - 1:
                col_up_value = self.get_cell_value(row-1, col)
                if col_up_value is not None:
                    value = col_up_value.split('\\')
                    cell_options[cell] = [int(value[0])]
                    value_one_solution = True

             #-----------------MAS DE UNA SOLUCION SUMAS MENORES A 10-----------------
            sum_row = []
            sum_col = []
            if value_one_solution is False:
                # FILAS
                for i in range(col, -1, -1):
                    value_sum = self.get_cell_value(row, i)
                    if value_sum != None:
                        break
                value_sum = value_sum.split('\\')
                if int(value_sum[1]) < 10:
                    sum_row = list(range(1, int(value_sum[1])))
                # COLUMNAS
                for i in range(row, -1, -1):
                    value_sum = self.get_cell_value(i, col)
                    if value_sum != None:
                        break
                value_sum = value_sum.split('\\')
                if int(value_sum[0]) < 10:
                    sum_col = list(range(1, int(value_sum[0])))
                
                #intercepcion entre sum_row y sum_col
                if sum_row and sum_col:
                    cell_options[cell] = list(set(sum_row) & set(sum_col))
                elif sum_row:
                    cell_options[cell] = sum_row
                elif sum_col:
                    cell_options[cell] = sum_col
                
        return cell_options
    
    def solve_kakkuro(self):
        empty_cells = []  # Almacenar las coordenadas de las celdas vacías
        for i in range(len(self.random_matrix)):
            for j in range(len(self.random_matrix[i])):
                if self.random_matrix[i][j] == '0':  # Celda vacía donde irían los posibles valores
                    empty_cells.append((i, j))

        cell_options = self.get_cell_options(empty_cells)
        print(f'cell_opt {cell_options}')
        # Ordenar las celdas vacías por el número de opciones posibles
        empty_cells.sort(key=lambda cell: len(cell_options[cell]))
        print(f'empty {empty_cells}')
        found_solution = False
        print("Iterar: ",*[cell_options[cell] for cell in empty_cells])

        # Probar cada combinación de números en las celdas vacías hasta encontrar una solución válida
        for combination in itertools.product(*[cell_options[cell] for cell in empty_cells]):
            temp_matrix = [row[:] for row in self.random_matrix]  # Crear una copia temporal del tablero
            
            for index, (row, col) in enumerate(empty_cells):
                temp_matrix[row][col] = str(combination[index])  # Probar cada combinación de números en el tablero  

            if self.is_valid_kakkuro(temp_matrix, self.random_matrix):  # Verificar si la combinación es válida
                found_solution = True
                return temp_matrix  # Devolver la solución encontrada

        return None  # Devolver None si no se encontró una solución válida

if __name__ == "__main__":
    root = tk.Tk()
    game = KakkuroGame(root)
    root.mainloop()
