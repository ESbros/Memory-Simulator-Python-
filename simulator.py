import numpy as np
import sys

Arguments = sys.argv

data = Arguments[1]
version = Arguments[2]
debug = len(sys.argv)
file = open(data)


# /---------------------------  Version 1  -----------------------------------/
if version == '1':
    tlb = np.zeros((32,4))
    list = file.readlines()
    fault = 0
    clean = 1
    writting = 0
    numline = 0

    def search_page(proc, dir, tlb):
        i = 0
        pos = -1
        for line in tlb:
            if line[0] == proc and line[1] == dir:
                pos = i
            i += 1
        return(pos)


    def updateReplace(pos, proc, dir, dirty, tlb):
        tlb[pos][0] = proc
        tlb[pos][1] = dir
        tlb[pos][2] = 1
        tlb[pos][3] = dirtyF_replace(pos, dirty, tlb)


    def updateFound(pos, proc, dir, dirty, tlb):
        tlb[pos][0] = proc
        tlb[pos][1] = dir
        tlb[pos][2] = 1
        tlb[pos][3] = dirtyF_found(pos, dirty, tlb)


    def replace(proc, dir, dirty, tlb, writting):
        res = type_replF(0, 0, tlb)
        if res[0] != 1:
            res = type_replF(0, 1, tlb)
        if res[0] != 1:
            res = type_replF(1, 0, tlb)
        if res[0] != 1:
            res = type_replF(1, 1, tlb)

        if tlb[res[1]][3] == 1:
            writting += 1

        updateReplace(res[1], proc, dir, dirty, tlb)
        return(res[1], writting)


    def type_replF(r, d, tlb):
        type_repl = 0
        pos = 0
        for line in tlb:
            if line[2] == r and line[3] == d:
                type_repl = 1
                break
            pos += 1
        return([type_repl, pos])


    def dirtyF_replace(pos, dirty, tlb):
        bit = tlb[pos][3]
        if bit == 0 and dirty == 'W':
            bit = 1
        elif bit == 1 and dirty == 'R':
            bit = 0
        return(bit)


    def dirtyF_found(pos, dirty, tlb):
        bit = tlb[pos][3]
        if bit == 0 and dirty == 'W':
            bit = 1
        return(bit)

    # Main Loop
    for row in list:

        split_row = row.split()
        proc = int(split_row[0])
        dir_inst = int(split_row[1]) // 512
        ref_mem = int(split_row[2]) // 512
        dirty = split_row[3]
        dirtyT = 'R'

        # Direccion Instruccion
        found = search_page(proc, dir_inst, tlb)
        if found != -1:
            updateFound(found, proc, dir_inst, dirtyT, tlb)
        else:
            pos, writting = replace(proc, dir_inst, dirtyT, tlb, writting)
            fault += 1
            if debug > 3:
                print('Linea Fallo:' + str(numline) + ' Frame Reemplazdo:' + str(pos) + ' ID:' + str(proc) + ' Pagina Logica:' + str(ref_mem) + ' Dirty:' + str(dirty))
                print('\n')

        # Referecia Memoria
        found = search_page(proc, ref_mem, tlb)
        if found != -1:
            updateFound(found, proc, ref_mem, dirty, tlb)
        else:
            pos, writting = replace(proc, ref_mem, dirty, tlb, writting)
            fault += 1
            if debug > 3:
                print('Linea Fallo:' + str(numline) + ' Frame Reemplazdo:' + str(pos) + ' ID:' + str(proc) + ' Pagina Logica:' + str(ref_mem) + ' Dirty:' + str(dirty))
                print('\n')

        if clean%200 == 0:
            clean = 0
            for line in tlb:
                line[2] = 0

        clean += 1

    file.close

    print('Page Faults: '+ str(fault))
    print('Writings: ' + str(writting))
    print("This is the name of the script: " +  sys.argv[0])
    print("Number of arguments: " + str(len(sys.argv)))
    print("The arguments are: " + str(sys.argv))


# /---------------------------  Version 2  -----------------------------------/
elif version == '2':
    tbl = np.zeros((32,4))

    for x in range(32):
        for y in range(4):
            tbl[x][y] = -1
            tbl[x][y] = -1
            tbl[x][y] = -1
            tbl[x][y] = -1

    list = file.readlines()
    fault = 0
    write = 0

    def place(pos, dirty, clock, tbl):
        if tbl[pos][2] == 0:
            tbl[pos][2] = dirty
        else:
            tbl[pos][2] == 1
        tbl[pos][3] = clock


    def searchpage(proc, page, tbl):
        pos = -1
        for x in range(32):
            if tbl[x][0] == proc and tbl[x][1] == page:
                pos = x
                return pos
        return pos


    def full(tbl):
        for x in range(32):
            if tbl[x][0] == -1:
                return x
        return -1


    def replaceempty(positionemptyspace, proc, page, dirty, clock, tbl):
        tbl[positionemptyspace][0] = proc
        tbl[positionemptyspace][1] = page
        tbl[positionemptyspace][2] = dirty
        tbl[positionemptyspace][3] = clock


    def findvictim(tbl):
        pos = 0
        minclock = tbl[0][3]
        for x in range(32):
            if tbl[x][3] < minclock:
                minclock = tbl[x][3]
                pos = x
        return pos


    def replacev2(pos, proc, page, dirty, clock, tbl):
        tbl[pos][0] = proc
        tbl[pos][1] = page
        tbl[pos][2] = dirty
        tbl[pos][3] = clock


    clock = 1
    for row in list:
        split_row = row.split()
        proc = int(split_row[0])
        page = int(split_row[1]) // 512
        page2 = int(split_row[2]) // 512

        found = searchpage(proc, page, tbl)
        dirty = 0
        if found != -1:
            place(found, dirty, clock ,tbl)
        else:
            fault = fault + 1
            positionemptyspace = full(tbl)
            if positionemptyspace != -1: #tabla con al menos un espacio vacio
                if debug > 3:
                   print('Linea de fallo:' + str(clock) + ' Reemplazando en frame:' + str(positionemptyspace) + ' Proceso:' + str(proc) + ' Pagina logica:' + str(page) + ' Dirty:' + str(tbl[positionemptyspace][2]))
                replaceempty(positionemptyspace, proc, page, dirty, clock, tbl)
            else: #tabla llena
                victim = findvictim(tbl)
                if debug > 3:
                    print('Linea de fallo:' + str(clock) + ' Reemplazando en frame:' + str(victim) + ' Proceso:' + str(proc) + ' Pagina logica:' + str(page) + ' Dirty:' + str(tbl[victim][2]))
                if tbl[victim][2] == 1:
                    write = write + 1
                replacev2(victim, proc, page, dirty, clock, tbl)


        found = searchpage(proc, page2, tbl)
        dirty = split_row[3]
        if dirty == "W":
            dirty = 1
        else:
            dirty = 0
        if found != -1:
            place(found, dirty, clock ,tbl)
        else:
            fault = fault + 1
            positionemptyspace = full(tbl)
            if positionemptyspace != -1: #tabla con al menos un espacio vacio
                if debug > 3:
                    print('Linea de fallo:' + str(clock) + ' Reemplazando en frame:' + str(positionemptyspace) + ' Proceso:' + str(proc) + ' Pagina logica:' + str(page2) + ' Dirty:' + str(tbl[positionemptyspace][2]))
                replaceempty(positionemptyspace, proc, page2, dirty, clock, tbl)
            else: #tabla llena
                victim = findvictim(tbl)
                if debug > 3:
                    print('Linea de fallo:' + str(clock) + ' Reemplazando en frame:' + str(victim) + ' Proceso:' + str(proc) + ' Pagina logica:' + str(page) + ' Dirty:' + str(tbl[victim][2]))
                if tbl[victim][2] == 1:
                    write = write + 1
                replacev2(victim, proc, page2, dirty, clock, tbl)
        clock = clock + 1

    file.close

    #for i in range(len(tbl)):
    #    print(tbl[i])

    print('Page Faults: '+ str(fault))
    print('Writings: ' + str(write))
    print("This is the name of the script: " +  sys.argv[0])
    print("Number of arguments: " + str(len(sys.argv)))
    print("The arguments are: " + str(sys.argv))
