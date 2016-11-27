'''
@author: Logan Finlayson
lfin100
2969317
'''

import drive

class Volume:

    vdrive = None
    NEW_VOLUME = ('+' + 127*'-' +  6* ('f:         0000:' + 12* '000 '))
    NEW_DIR = (8*('f:         0000:' + 12* '000 '))
    NEW_ENTRY = ('f:         0000:' + 12* '000 ')

    def format(self, name):
        '''Formats the drive then sets up initial root dir'''
        self.vdrive = drive.Drive(name)
        self.vdrive.format()
        self.vdrive.write_block(0, Volume.NEW_VOLUME)

    def disconnect(self):
        '''Disconnects and sets volumes vdrive to None'''
        self.vdrive.disconnect()
        self.vdrive = None

    def reconnect(self, drivename):
        '''Given a name, reconnects to a previous drive'''
        if self.vdrive != None:
            self.disconnect()

        self.vdrive = drive.Drive(drivename)
        try:
            self.vdrive.reconnect()
        except IOError:
            print('Warning! File does not exist. Currently not connected to any drives.')
            self.vdrive = None


    def read(self, block):
        '''Direct call to drives read_block'''
        return self.vdrive.read_block(block)

    def write(self, block, data):
        '''Uses drives write_block, and ensures that the byte length is at least 512'''
        padding_length = 512 - len(data)
        new_data = data + ' ' * padding_length
        self.vdrive.write_block(block, new_data)



    def mkdir(self, pathname):
        '''
        Takes a path name, and attempts to create a new directory
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Did not complete directory creation.')
            return

        parent_block = 0
        grandparent_block = 0 #to keep track of "previous" parent block, if we need to go back

        for i in range(len(namelist)):
            if i == len(namelist)-1: #if it's the last name in the list, then we're in the directory we need to be in.
                name = namelist[i]

            else:
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8-len(dir))*' ')

                if dir_loc == -1:
                    print('Warning: pathname not valid. Did not complete directory creation.')
                    return
                parent_size = int(parent_dir_data[dir_loc+11:dir_loc+15])
                parent_num_blocks = int(parent_size/512)

                if parent_num_blocks == 0: #no blocks allocated yet to the dir we want to create in, need to allocate block for dir
                    block = self.findFreeBlock()
                    if block == -1:
                        print('Warning. No blocks left to write to!')
                        return

                    self.write(block, self.NEW_DIR)
                    parent_dir_data = parent_dir_data[:dir_loc+11] + '0512:' + (3-len(str(block)))*'0' + str(block) + parent_dir_data[dir_loc+19:]
                    self.write(parent_block, parent_dir_data)

                    root_data = self.read(0)
                    root_data = root_data[:block] + '+' + root_data[block + 1:]
                    self.write(0, root_data)

                    grandparent_block = parent_block
                    parent_block = block

                else:
                    grandparent_block = parent_block
                    if i == len(namelist)-2:
                        parent_block = self.find_next_block(dir, 'f:        ', parent_block)
                        if parent_block == -1:
                            parent_block = int(parent_dir_data[dir_loc + 16 + ((parent_num_blocks - 1) * 4):dir_loc + 19 + ((parent_num_blocks - 1) * 4)])

                    else:
                        parent_block = self.find_next_block(dir, 'd:'+namelist[i+1], parent_block) #need to find which block the next name is in
                        if parent_block == -1:
                            print('Warning: pathname not valid. Did not complete directory creation.')
                            return


        if len(name) > 8:
            print('Warning: Name greater than 8 characters. Did not complete directory creation.')
            return
        name = name + (8-len(name))* ' '

        parent_dir_data = self.read(parent_block)
        free_spot = parent_dir_data.find('f:         0000:000')

        if free_spot == -1: #No free spot in current directory, need to allocate new block to dir
            if parent_block == 0:
                print('The root directory "/" is at full capacity. Cannot proceed.')
                return
            grandparent_dir_data = self.read(grandparent_block)

            block = self.findFreeBlock()
            if block == -1:
                print('Warning. No blocks left to write to!')
                return
            self.write(block, self.NEW_DIR)

            new_size = parent_size + 512
            if new_size == 512*13:
                print("Warning: The directory you are wanting to create a new directory in is already at full capacity!")
                return

            grandparent_dir_data = grandparent_dir_data[:dir_loc + 11] + (4 - len(str(new_size))) * '0' + str(new_size) + grandparent_dir_data[dir_loc+15:dir_loc+16+(parent_num_blocks*4)] + (3 - len(str(block))) * '0' + str(block) + grandparent_dir_data[dir_loc + 19 + (parent_num_blocks*4):]
            self.write(grandparent_block, grandparent_dir_data)

            root_data = self.read(0)
            root_data = root_data[:block] + '+' + root_data[block + 1:]
            self.write(0, root_data)

            parent_block = block
            parent_dir_data = self.read(parent_block)
            free_spot = parent_dir_data.find('f:         0000:000')

        parent_dir_data = parent_dir_data[:free_spot] + 'd:' + name + parent_dir_data[free_spot + 10:]
        self.write(parent_block, parent_dir_data)



    def mkfile(self, pathname):
        '''
        Takes a pathname, and attempts to create a new file
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Did not complete file creation.')
            return

        parent_block = 0
        grandparent_block = 0 #keep track of 'previous' parent block

        for i in range(len(namelist)):
            if i == len(namelist) - 1: #At the end of the list, name of file we want to create
                name = namelist[i]
            else:
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')

                if dir_loc == -1:
                    print('Warning: pathname not valid. Did not complete file creation.')
                    return
                parent_size = int(parent_dir_data[dir_loc + 11:dir_loc + 15])
                parent_num_blocks = int(parent_size / 512)

                if parent_num_blocks == 0: #no blocks allocated yet, need to allocate block for dir
                    block = self.findFreeBlock()
                    if block == -1:
                        print('Warning. No blocks left to write to!')
                        return
                    self.write(block, self.NEW_DIR)

                    parent_dir_data = parent_dir_data[:dir_loc + 11] + '0512:' + (3 - len(str(block))) * '0' + str(block) + parent_dir_data[dir_loc + 19:]
                    self.write(parent_block, parent_dir_data)

                    root_data = self.read(0)
                    root_data = root_data[:block] + '+' + root_data[block + 1:]
                    self.write(0, root_data)

                    grandparent_block = parent_block
                    parent_block = block

                else:
                    grandparent_block = parent_block

                    if i == len(namelist)-2:
                        parent_block = self.find_next_block(dir, 'f:        ', parent_block)
                        if parent_block == -1:
                            parent_block = int(parent_dir_data[dir_loc + 16 + ((parent_num_blocks - 1) * 4):dir_loc + 19 + ((parent_num_blocks - 1) * 4)])

                    else:
                        parent_block = self.find_next_block(dir, 'd:'+namelist[i + 1], parent_block) #need to find which block the next name we are looking for is
                        if parent_block == -1:
                            print('Warning: pathname not valid. Did not complete file creation.')
                            return

        if len(name) > 8:
            print('Warning: Name greater than 8 characters. Did not complete file creation.')
            return
        name = name + (8-len(name))* ' '

        parent_dir_data = self.read(parent_block)
        free_spot = parent_dir_data.find('f:         0000:000')

        if free_spot == -1: #no free spot left in current directory, need to allocate new block for directory
            if parent_block == 0:
                print('The root directory "/" is at full capacity. Cannot proceed.')
                return

            grandparent_dir_data = self.read(grandparent_block)
            block = self.findFreeBlock()
            if block == -1:
                print('Warning. No blocks left to write to!')
                return
            self.write(block, self.NEW_DIR)

            new_size = parent_size + 512
            if new_size == 512 * 13:
                print("Warning: The directory you are wanting to create a new file in is already at full capacity!")
                return

            grandparent_dir_data = grandparent_dir_data[:dir_loc + 11] + (4 - len(str(new_size))) * '0' + str(new_size) + grandparent_dir_data[dir_loc + 15:dir_loc + 16 + (parent_num_blocks * 4)] + (3 - len(str(block))) * '0' + str(block) + grandparent_dir_data[dir_loc + 19 + (parent_num_blocks * 4):]
            self.write(grandparent_block, grandparent_dir_data)

            root_data = self.read(0)
            root_data = root_data[:block] + '+' + root_data[block + 1:]
            self.write(0, root_data)

            parent_block = block
            parent_dir_data = self.read(parent_block)
            free_spot = parent_dir_data.find('f:         0000:000')

        parent_dir_data = parent_dir_data[:free_spot + 2] + name + parent_dir_data[free_spot + 10:]
        self.write(parent_block, parent_dir_data)



    def append(self, pathname, data):
        '''
        Takes the pathname of a file, and some data, and attempts to append the data to the end of the file
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Cannot append file.')
            return

        parent_block = 0
        for i in range(len(namelist)):
            if i == len(namelist) - 1: #found the file we want to append
                name = namelist[i]
            else:                       #go through directories until we are in the correct one for the file we want to append
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')
                if dir_loc == -1:
                    print('Warning: pathname not valid. Cannot append file.')
                    return
                if i == len(namelist) - 2:
                    parent_block = self.find_next_block(dir, 'f:'+namelist[i+1],  parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot append file.')
                        return
                else:
                    parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1],  parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot append file.')
                        return


        file_name = 'f:' + name + (8-len(name)) * ' '

        parent_dir_data = self.read(parent_block)
        file_spot = parent_dir_data.find(file_name)
        if file_spot == -1:
            print('Warning: pathname not valid. Cannot append file.')
            return

        file_size = int(parent_dir_data[file_spot+11:file_spot+15])

        blocklist = []
        for i in range(0,12):
            blocklist.append(int(parent_dir_data[file_spot+16+(i*4):file_spot+19+(i*4)]))

        try:
            num_blocks = blocklist.index(0)
        except ValueError:
            num_blocks = 12
        new_block = False

        if (file_size + len(data)) > num_blocks*512: #Need to allocate new block for file.
            if num_blocks == 12:
                print('Warning: Writing this to the file will put it over its block limit. Did not append file!')
                return
            block = self.findFreeBlock()
            if block == -1:
                print('Warning. No blocks left to write to!')
                return

            parent_dir_data = parent_dir_data[:file_spot + 16+(num_blocks*4)] + (3 - len(str(block))) * '0' + str(block) + parent_dir_data[file_spot + 19 + (num_blocks*4):]
            self.write(parent_block, parent_dir_data)

            root_data = self.read(0)
            root_data = root_data[:block] + '+' + root_data[block + 1:]
            self.write(0, root_data)
            new_block = True

            blocklist = []
            for i in range(0, 12):
                blocklist.append(int(parent_dir_data[file_spot + 16 + (i * 4):file_spot + 19 + (i * 4)]))



        parent_dir_data = self.read(parent_block)
        parent_dir_data = parent_dir_data[:file_spot+11] + (4-len(str(len(data)+file_size)))*'0' + str(len(data)+file_size) + parent_dir_data[file_spot+15:]
        self.write(parent_block, parent_dir_data)


        if (new_block == False): #if we didn't allocate a new block, can just write simply
            try:
                num_blocks = blocklist.index(0)
            except ValueError:
                num_blocks = 12
            current_block = num_blocks - 1
            file_block = blocklist[current_block]
            file_data = self.read(file_block)
            file_data = file_data[:file_size%512] + data + file_data[file_size%512+len(data):]
            self.write(file_block, file_data)

        else:   #if we did allocate a new block, need to split data up into parts that will go into next block and current block
            try:
                num_blocks = blocklist.index(0)
            except ValueError:
                num_blocks = 12
            current_block = num_blocks - 2
            next_block = num_blocks - 1
            if current_block == -1:
                current_block = 0

            n_file_block = blocklist[next_block]
            n_file_data = self.read(n_file_block)
            n_file_data = data[512 - (file_size % 512):]
            self.write(n_file_block, n_file_data)

            c_file_block = blocklist[current_block]
            c_file_data = self.read(c_file_block)
            c_file_data = c_file_data[:file_size%512] + data[:512-(file_size%512)]
            self.write(c_file_block, c_file_data)



    def ls(self, pathname):
        '''
        Takes the pathname of a directory, and lists the directory contents
        '''
        if pathname == '/': #different for root dir
            print('\nDirectory: ' + pathname)
            print('Name     Type Size')
            print('----     ---- ----')
            root_data = self.read(0)
            for i in range(0,6):
                if root_data[130+(64*i):138+(64*i)] != '        ':
                    print(root_data[130+(64*i):138+(64*i)] + '  ' + root_data[128+(64*i):130+(64*i)] + '  ' + str(int(root_data[139+(64*i):143+(64*i)])))
            print()

        else:
            namelist = self.splitPathname(pathname)

            if len(namelist) == 0:
                print('Warning: pathname not valid. Cannot ls.')
                return

            parent_block = 0
            for i in range(len(namelist)): #navigating to correct dir
                if i == len(namelist) - 1:
                    name = namelist[i]
                else:
                    parent_dir_data = self.read(parent_block)
                    dir = namelist[i]
                    dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')
                    if dir_loc == -1:
                        print('Warning: pathname not valid. Cannot ls.')
                        return
                    if i == len(namelist) - 2:
                        parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                        if parent_block == -1:
                            print('Warning: pathname not valid. Cannot ls.')
                            return
                    else:
                        parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                        if parent_block == -1:
                            print('Warning: pathname not valid. Cannot ls.')
                            return


            dir_name = 'd:' + name + (8 - len(name)) * ' '

            parent_dir_data = self.read(parent_block)

            file_spot = parent_dir_data.find(dir_name)
            if file_spot == -1:
                print('Warning: filename not valid. Cannot ls.')
                return

            print('\nDirectory: ' + pathname)
            print('Name     Type Size')
            print('----     ---- ----')

            file_size = int(parent_dir_data[file_spot + 11:file_spot + 15])
            if file_size == 0:
                return

            blocklist = []
            for i in range(0, 12):
                block = int(parent_dir_data[file_spot + 16 + (i * 4):file_spot + 19 + (i * 4)])
                if block != 0:
                    blocklist.append(block)

            for i in blocklist:
                data = self.read(i)
                for i in range(0, 8):
                    if data[2 + (64 * i):10 + (64 * i)] != '        ':
                        print(data[2 + (64 * i):10 + (64 * i)] + '  ' + data[0 + (64 * i):2 + (64 * i)] + '  ' + str(int(data[11 + (64 * i):15 + (64 * i)])))
            print()


    def vprint(self, pathname):
        '''
        Takes the pathname of a file, and prints the contents of the file
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Cannot print.')
            return

        parent_block = 0
        for i in range(len(namelist)): #navigating to correct dir
            if i == len(namelist) - 1:
                name = namelist[i]
            else:
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')
                if dir_loc == -1:
                    print('Warning: pathname not valid. Cannot print.')
                    return
                if i == len(namelist) - 2:
                    parent_block = self.find_next_block(dir, 'f:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot print.')
                        return
                else:
                    parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot print.')
                        return

        file_name = 'f:' + name + (8 - len(name)) * ' '

        parent_dir_data = self.read(parent_block)
        file_spot = parent_dir_data.find(file_name)
        if file_spot == -1:
            print('Warning: filename not valid. Cannot print.')
            return

        file_size = int(parent_dir_data[file_spot + 11:file_spot + 15])
        if file_size == 0:
            print('\n')
            return

        blocklist = []
        for i in range(0, 12):
            block = int(parent_dir_data[file_spot + 16 + (i * 4):file_spot + 19 + (i * 4)])
            if block != 0:
                blocklist.append(block)
        printed_string = ''
        for i in blocklist:
            if i == blocklist[-1]:
                printed_string += self.read(i)[:file_size%512]
            else:
                printed_string += self.read(i)
        print(printed_string)



    def delfile(self, pathname):
        '''
        Takes the pathname of a file, and deletes it from the drive
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Cannot delete file.')
            return

        parent_block = 0
        for i in range(len(namelist)): #navigating to correct dir
            if i == len(namelist) - 1:
                name = namelist[i]
            else:
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')
                if dir_loc == -1:
                    print('Warning: pathname not valid. Cannot delete file.')
                    return
                if i == len(namelist) - 2:
                    parent_block = self.find_next_block(dir, 'f:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot delete file.')
                        return
                else:
                    parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot delete file.')
                        return

        file_name = 'f:' + name + (8 - len(name)) * ' '

        parent_dir_data = self.read(parent_block)
        file_spot = parent_dir_data.find(file_name)
        if file_spot == -1:
            print('Warning: filename not valid. Cannot delete file.')
            return

        blocklist = []
        for i in range(0, 12):
            block = int(parent_dir_data[file_spot + 16 + (i * 4):file_spot + 19 + (i * 4)])
            if block != 0:
                blocklist.append(block)

        root_data = self.read(0)
        for i in blocklist:
            self.write(i, 512*' ')
            root_data = root_data[:i] + '-' + root_data[i+1:]
        self.write(0, root_data)

        parent_dir_data = parent_dir_data[:file_spot] + self.NEW_ENTRY + parent_dir_data[file_spot+64:]
        self.write(parent_block, parent_dir_data)



    def deldir(self, pathname):
        '''
        Takes the pathname of a directory, and, if it is empty, deletes it from the drive
        '''
        namelist = self.splitPathname(pathname)
        if len(namelist) == 0:
            print('Warning: pathname not valid. Cannot delete directory.')
            return

        parent_block = 0
        for i in range(len(namelist)): #navigating to correct dir
            if i == len(namelist) - 1:
                name = namelist[i]
            else:
                parent_dir_data = self.read(parent_block)
                dir = namelist[i]
                dir_loc = parent_dir_data.find('d:' + dir + (8 - len(dir)) * ' ')
                if dir_loc == -1:
                    print('Warning: pathname not valid. Cannot delete directory.')
                    return
                if i == len(namelist) - 2:
                    parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot delete directory.')
                        return
                else:
                    parent_block = self.find_next_block(dir, 'd:' + namelist[i + 1], parent_block)
                    if parent_block == -1:
                        print('Warning: pathname not valid. Cannot delete directory.')
                        return

        dir_name = 'd:' + name + (8 - len(name)) * ' '

        parent_dir_data = self.read(parent_block)
        dir_spot = parent_dir_data.find(dir_name)
        if dir_spot == -1:
            print('Warning: filename not valid. Cannot delete directory.')
            return

        blocklist = []
        for i in range(0, 12):
            block = int(parent_dir_data[dir_spot + 16 + (i * 4):dir_spot + 19 + (i * 4)])
            if block != 0:
                blocklist.append(block)

        for i in blocklist:
            if self.read(i) != self.NEW_DIR:
                print('Warning. Directory not empty. Cannot delete directory')
                return

        root_data = self.read(0)
        for i in blocklist:
            self.write(i, 512 * ' ')
            root_data = root_data[:i] + '-' + root_data[i + 1:]
        self.write(0, root_data)

        parent_dir_data = parent_dir_data[:dir_spot] + self.NEW_ENTRY + parent_dir_data[dir_spot + 64:]
        self.write(parent_block, parent_dir_data)



    def find_next_block(self, dir_name, next_name, parent_block):
        '''
        Given two names (the directory you want to search, and the name you want to find) and the block in which the
        the directory you are looking in resides, find and return the block of the name you want to find.
        '''
        parent_dir_data = self.read(parent_block)

        dir_loc = parent_dir_data.find('d:' + dir_name + (8-len(dir_name))* ' ')

        blocklist = []
        for i in range(0, 12):
            block = int(parent_dir_data[dir_loc + 16 + (i * 4):dir_loc + 19 + (i * 4)])
            if block != 0:
                blocklist.append(block)
        for i in blocklist:
            dir_data = self.read(i)
            if next_name == 'f:        ':
                next_loc = dir_data.find(next_name + (10 - len(next_name)) * ' ')
            else:
                next_loc = dir_data.find(next_name + (10 - len(next_name)) * ' ')
            if next_loc != -1:
                return i
        return -1


    def findFreeBlock(self):
        '''
        Looks through the bitmap header and finds and returns a free block
        '''
        bitmap = self.vdrive.read_block(0)[:128]
        block = bitmap.find('-')
        return block


    def splitPathname(self, pathname):
        '''
        Splits a pathname string into a list of directory/file names
        '''
        list = []
        if pathname[0] != '/':
            return list
        pntr = 1

        while (pntr < len(pathname)):
            newpntr = pathname[pntr:].find('/')
            if newpntr != -1:
                newpntr = newpntr + pntr
                list.append(pathname[pntr:newpntr])
                pntr = newpntr + 1
            else:
                list.append(pathname[pntr:])
                pntr = len(pathname)

        return list
