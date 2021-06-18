import os
import curses
import pycfg
from pyarch import load_binary_into_memory
from pyarch import cpu_t

class os_t:
	def __init__ (self, cpu, memory, terminal):
		self.cpu = cpu
		self.memory = memory
		self.terminal = terminal

		self.terminal.enable_curses()

		self.console_str = ""
		self.terminal.console_print("this is the console, type the commands here\n")

	def printk(self, msg):
		self.terminal.kernel_print("\n" + "kernel: " + msg)

	def panic (self, msg):
		self.terminal.end()
		self.terminal.dprint("kernel panic: " + msg)
		self.cpu.cpu_alive = False
		#cpu.cpu_alive = False

	# handles and treat commands
	def command_prompt(self):
		# gets console entry; removes white spaces from begin and end; puts it on console_entry variable
		console_entry = self.console_str.strip()

		# terminate method if entry without white spaces are void
		if len(console_entry) <= 0:
			return 
		
		console_entry = console_entry.split() # splits command and arguments by white spaces
		cmd = console_entry[0] # gets command
		cmd_arguments = console_entry[1:] # gets command arguments

		# checks if command is "exit"
		if cmd == "exit":
			# execute cmd_exit method if command is "exit" and have no arguments
			if len(cmd_arguments) == 0:
				self.cmd_exit()
				return
			# else print a message saying the "exit" command takes no arguments
			else:
				self.terminal.console_print("\r" + "exit: takes no arguments" + "\n")
				return 
		# checks if command is lp (load process)
		elif cmd == "lp":
			# checks for arguments
			if len(cmd_arguments) > 0:
				# gets process file name
				process_file_name = cmd_arguments[0]

				# checks for the dot (.) in process file name
				if process_file_name.find('.') > -1:
					process_file_name = process_file_name.split('.') # splits process file name by the dot (.)
					process_name = process_file_name[0] # get process name
					process_ext = process_file_name[1] # get process extension
					
					# checks for ".asm" process extension then execute label message saying process successfully loaded
					# here will be executed method to load a process (later)
					if process_ext == "asm":
						self.terminal.console_print("\r" + process_name + "." + process_ext + " successfully loaded!" + "\n")
						return
					# else print a message saying that the unknown extension 
					else:
						self.terminal.console_print("\r" + 'lp: "' + '.' + process_ext + '"' + " -> unknown extension")
						return
				# else print a message saying that is missing process extension
				else:
					self.terminal.console_print("\r"  + 'lp: "' + process_file_name + '"' + " -> missing process extension")
					return
			# else print a message saying that is missing process argument
			else:
				self.terminal.console_print("\r" + "lp: missing process argument" + "\n")
				return
		# else print a message saying that typed command not found 
		else:
			self.terminal.console_print("\r" + cmd + ": command not found!" + "\n")
			return

	# ends simulation
	def cmd_exit(self):
		self.terminal.end()
		self.terminal.dprint("Ending simulation")
		self.cpu.cpu_alive = False

	def interrupt_keyboard (self):
		key = self.terminal.get_key_buffer()

		if ((key >= ord('a')) and (key <= ord('z'))) or ((key >= ord('A')) and (key <= ord('Z'))) or ((key >= ord('0')) and (key <= ord('9'))) or (key == ord(' ')) or (key == ord('-')) or (key == ord('_')) or (key == ord('.')):
			self.console_str += chr(key)
			self.terminal.console_print("\r" + self.console_str)

		elif key == curses.KEY_BACKSPACE:
			self.console_str = self.console_str[:-1]
			self.terminal.console_print("\r" + self.console_str)
			return

		elif (key == curses.KEY_ENTER) or (key == ord('\n')):
			self.terminal.console_print("\n")
			self.command_prompt()
			self.console_str = "" # apaga informacoes de input
			return

	def handle_interrupt (self, interrupt):
		if interrupt == pycfg.INTERRUPT_KEYBOARD:
			self.interrupt_keyboard()
			self.printk(f'{interrupt}:(Keybord) interrupt')
		elif interrupt == pycfg.INTERRUPT_MEMORY_PROTECTION_FAULT:
			self.printk(f'{interrupt}:(Memory fault) interrupt not implemented')
		elif interrupt == pycfg.INTERRUPT_TIMER:
			self.printk(f'{interrupt}:(Timer) interrupt not implemented')
		else:
			self.printk('Interrupt not implemented')
		return

	def syscall (self):
		self.printk('Syscall not implemented')
		#self.terminal.app_print(msg)
		return

class process_t:
	def __init__(self, name):
		self.regs = [0,0,0,0,0,0,0,0]
		self.reg_pc = 0
		self.state = 0
		self.name = name
