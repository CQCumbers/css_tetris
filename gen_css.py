import itertools

# common logical operations

def and_p(lhs, rhs, i):
    return f'var(--{lhs}_{i}p) var(--{rhs}_{i}p)'

def and_n(lhs, rhs, i):
    return f'var(--{lhs}_{i}n, var(--{rhs}_{i}n))'

def or_p(lhs, rhs, i):
    return f'var(--{lhs}_{i}p, var(--{rhs}_{i}p))'

def or_n(lhs, rhs, i):
    return f'var(--{lhs}_{i}n) var(--{rhs}_{i}n)'

def xor_p(lhs, rhs, i):
    p1 = f'var(--{lhs}_{i}p, var(--{rhs}_{i}p))'
    p2 = f'var(--{lhs}_{i}n, var(--{rhs}_{i}n))'
    return f'{p1} {p2}'

def xor_n(lhs, rhs, i):
    p1 = f'var(--{lhs}_{i}p, var(--{rhs}_{i}n))'
    p2 = f'var(--{lhs}_{i}n, var(--{rhs}_{i}p))'
    return f'{p1} {p2}'

def ant_p(lhs, rhs, i):
    return f'var(--{lhs}_{i}p) var(--{rhs}_{i}n)'

def ant_n(lhs, rhs, i):
    return f'var(--{lhs}_{i}n, var(--{rhs}_{i}p))'

# CPU components

def emit_inc(out, inp, cin, n):
    print(f'  /* {out} = {inp} + 1 */')
    print(f'  --{cin}_0p: /**/;')
    print(f'  --{cin}_0n: initial;')
    for i in range(n):
        print(f'  --{out}_{i}p: {xor_p(inp, cin, i)};')
        print(f'  --{out}_{i}n: {xor_n(inp, cin, i)};')
        print(f'  --{cin}_{i + 1}p: {and_p(inp, cin, i)};')
        print(f'  --{cin}_{i + 1}n: {and_n(inp, cin, i)};')

def emit_mov(out, rhs, n, mov_en):
    print(f'  /* {out} = {rhs} */')
    for i in range(n):
        print(f'  --{out}_{i}p: var(--{rhs}_{i}p) {mov_en};')
        print(f'  --{out}_{i}n: var(--{rhs}_{i}n) {mov_en};')

def emit_add(out, inp0, inp1, cin, n, alu_en):
    gout = f'{out}G'
    pout = f'{out}P'
    print(f'  /* {out} = {inp0} + {inp1} */')
    for i in range(n):
        print(f'  --{gout}_{i}p: {and_p(inp0, inp1, i)};')
        print(f'  --{pout}_{i}p: {xor_p(inp0, inp1, i)};')
        print(f'  --{pout}_{i}n: {xor_n(inp0, inp1, i)};')

    for i in range(n):
        resp = f'var(--{pout}_{i}p) var(--{cin}_{i}p)'
        print(f'  --{cin}_{i + 1}p: var(--{gout}_{i}p, {resp});')
        print(f'  --{cin}_{i + 1}n: {and_n(inp0, inp1, i)} {and_n(pout, cin, i)};')
    
    for i in range(n):
        print(f'  --{out}_{i}p: {xor_p(pout, cin, i)} {alu_en};')
        print(f'  --{out}_{i}n: {xor_n(pout, cin, i)} {alu_en};')

def emit_flip(out, inp, sel, n):
    print(f'  /* {out} = {sel} ? -{inp} : {inp} */')
    for i in range(n):
        print(f'  --{out}_{i}p: var(--{sel}p, var(--{inp}_{i}p)) var(--{sel}n, var(--{inp}_{i}n));')
        print(f'  --{out}_{i}n: var(--{sel}p, var(--{inp}_{i}n)) var(--{sel}n, var(--{inp}_{i}p));')

def emit_sel(out, inp0, inp1, sel, n, start=0):
    print(f'  /* {out} = {sel} ? {inp1} : {inp0} */')
    for i in range(start, n):
        p1 = f'var(--{sel}p, var(--{inp0}_{i}p))'
        n1 = f'var(--{sel}p, var(--{inp0}_{i}n))'
        print(f'  --{out}_{i}p: {p1} var(--{sel}n, var(--{inp1}_{i}p));')
        print(f'  --{out}_{i}n: {n1} var(--{sel}n, var(--{inp1}_{i}n));')

def emit_sll(out, inp0, inp1, sll_en):
    stages = ['', 'A', 'B', 'C']
    print(f'  /* {out} = {inp0} << {inp1} */')
    # check inp1 <= 15
    """
    for i in range(4, 16):
        in_rng = f'var(--{inp1}_{i}n) {in_rng}' if i > 4 else f'var(--{inp1}_4n)'
        out_rng = f'var(--{inp1}_{i}p, {out_rng})' if i > 4 else f'var(--{inp1}_4p)'
    for i in range(16):
        print(f'  --{out}D_{i}p: var(--{inp0}_{i}p) {in_rng};')
        print(f'  --{out}D_{i}n: var(--{inp0}_{i}n, {out_rng});')
    inp0 = f'{out}D'
    """
    # barrel shifter
    for j in range(4):
        stage = stages[3 - j]
        for i in range(16):
            if i - (8 >> j) < 0:
                p1 = f'var(--{inp1}_{3 - j}n) var(--{inp0}_{i}p)'
                p1 = f'{p1} {sll_en}' if j == 3 else p1
                print(f'  --{out}{stage}_{i}p: {p1};')
                n1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}n))'
                n1 = f'{n1} {sll_en}' if j == 3 else n1
                print(f'  --{out}{stage}_{i}n: {n1};')
            else:
                p1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}p))'
                p2 = f'var(--{inp1}_{3 - j}n, var(--{inp0}_{i - (8 >> j)}p))'
                p2 = f'{p2} {sll_en}' if j == 3 else p2
                print(f'  --{out}{stage}_{i}p: {p1} {p2};')
                n1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}n))'
                n2 = f'var(--{inp1}_{3 - j}n, var(--{inp0}_{i - (8 >> j)}n))'
                n2 = f'{n2} {sll_en}' if j == 3 else n2
                print(f'  --{out}{stage}_{i}n: {n1} {n2};')
        inp0 = f'{out}{stage}'

def emit_srl(out, inp0, inp1, srl_en):
    stages = ['', 'A', 'B', 'C']
    print(f'  /* {out} = {inp0} >> {inp1} */')
    # check inp1 <= 15
    """
    for i in range(4, 16):
        in_rng = f'var(--{inp1}_{i}n) {in_rng}' if i > 4 else f'var(--{inp1}_4n)'
        out_rng = f'var(--{inp1}_{i}p, {out_rng})' if i > 4 else f'var(--{inp1}_4p)'
    for i in range(16):
        print(f'  --{out}D_{i}p: var(--{inp0}_{i}p) {in_rng};')
        print(f'  --{out}D_{i}n: var(--{inp0}_{i}n, {out_rng});')
    inp0 = f'{out}D'
    """
    # barrel shifter
    for j in range(4):
        stage = stages[3 - j]
        for i in range(16):
            if i + (8 >> j) > 15:
                p1 = f'var(--{inp1}_{3 - j}n) var(--{inp0}_{i}p)'
                p1 = f'{p1} {srl_en}' if j == 3 else p1
                print(f'  --{out}{stage}_{i}p: {p1};')
                n1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}n))'
                n1 = f'{n1} {srl_en}' if j == 3 else n1
                print(f'  --{out}{stage}_{i}n: {n1};')
            else:
                p1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}p))'
                p2 = f'var(--{inp1}_{3 - j}n, var(--{inp0}_{i + (8 >> j)}p))'
                p2 = f'{p2} {srl_en}' if j == 3 else p2
                print(f'  --{out}{stage}_{i}p: {p1} {p2};')
                n1 = f'var(--{inp1}_{3 - j}p, var(--{inp0}_{i}n))'
                n2 = f'var(--{inp1}_{3 - j}n, var(--{inp0}_{i + (8 >> j)}n))'
                n2 = f'{n2} {srl_en}' if j == 3 else n2
                print(f'  --{out}{stage}_{i}n: {n1} {n2};')
        inp0 = f'{out}{stage}'

def emit_bitops(lhs, rhs, n, mux):
    for i in range(n):
        print(f'  --and_{i}p: {and_p(lhs, rhs, i)} var(--{mux}_4);')
        print(f'  --and_{i}n: {and_n(lhs, rhs, i)} var(--{mux}_4);')
        print(f'  --or_{i}p: {or_p(lhs, rhs, i)} var(--{mux}_5);')
        print(f'  --or_{i}n: {or_n(lhs, rhs, i)} var(--{mux}_5);')
        print(f'  --xor_{i}p: {xor_p(lhs, rhs, i)} var(--{mux}_6);')
        print(f'  --xor_{i}n: {xor_n(lhs, rhs, i)} var(--{mux}_6);')
        print(f'  --ant_{i}p: {ant_p(lhs, rhs, i)} var(--{mux}_7);')
        print(f'  --ant_{i}n: {ant_n(lhs, rhs, i)} var(--{mux}_7);')

def emit_mux(out, sel, n, romlen, start=0):
    print(f'  /* {out}_i = ({sel} == i) */')
    for idx in range(start, romlen):
        for i in range(n): 
            bit = f'{sel}_{i}p' if (idx >> i) & 1 else f'{sel}_{i}n'
            res = f'var(--{bit}) {res}' if i > 0 else f'var(--{bit})'
        print(f'  --{out}_{idx}: {res};')

def emit_mux_pn(out, sel, n, romlen):
    print(f'  /* {out}_i = ({sel} == i) */')
    for idx in range(romlen):
        for i in range(n): 
            bitp = f'{sel}_{i}p' if (idx >> i) & 1 else f'{sel}_{i}n'
            bitn = f'{sel}_{i}n' if (idx >> i) & 1 else f'{sel}_{i}p'
            resp = f'var(--{bitp}) {resp}' if i > 0 else f'var(--{bitp})'
            resn = f'var(--{bitn}, {resn})' if i > 0 else f'var(--{bitn})'
        print(f'  --{out}_{idx}p: {resp};')
        print(f'  --{out}_{idx}n: {resn};')

def emit_rom(filename, mux):
    # assumes emit_mux has already been called
    op_dict = {
        'MNZ': 0, 'MLZ': 1, 'ADD': 2, 'SUB': 3,
        'AND': 4, 'OR': 5, 'XOR': 6, 'ANT': 7,
        'SL': 8, 'SRL': 9, 'SRA': 10
    }
    i = 0
    print(f'  /* {filename} */')
    with open(filename, 'r') as rom:
        for line in rom:
            parts = line.replace(';', '').split()
            op = op_dict[parts[1]]
            for j in range(4):
                pbit = f'var(--{mux}_{i})' if (op >> j) & 1 else 'initial'
                nbit = 'initial' if (op >> j) & 1 else f'var(--{mux}_{i})'
                print(f'  --rom{i}_op_{j}p: {pbit};')
                print(f'  --rom{i}_op_{j}n: {nbit};')
            for k in range(3):
                addr = ''
                if parts[k + 2][0] == 'A':
                    print(f'  --rom{i}_type{k}_0p: var(--{mux}_{i});')
                    print(f'  --rom{i}_type{k}_0n: initial;')
                    print(f'  --rom{i}_type{k}_1p: initial;')
                    print(f'  --rom{i}_type{k}_1n: var(--{mux}_{i});')
                    addr = int(parts[k + 2][1:])
                elif parts[k + 2][0] == 'B':
                    print(f'  --rom{i}_type{k}_0p: initial;')
                    print(f'  --rom{i}_type{k}_0n: var(--{mux}_{i});')
                    print(f'  --rom{i}_type{k}_1p: var(--{mux}_{i});')
                    print(f'  --rom{i}_type{k}_1n: initial;')
                    addr = int(parts[k + 2][1:])
                else:
                    print(f'  --rom{i}_type{k}_0p: initial;')
                    print(f'  --rom{i}_type{k}_0n: var(--{mux}_{i});')
                    print(f'  --rom{i}_type{k}_1p: initial;')
                    print(f'  --rom{i}_type{k}_1n: var(--{mux}_{i});')
                    addr = int(parts[k + 2])
                for j in range(16):
                    pbit = f'var(--{mux}_{i})' if (addr >> j) & 1 else 'initial'
                    nbit = 'initial' if (addr >> j) & 1 else f'var(--{mux}_{i})'
                    print(f'  --rom{i}_addr{k}_{j}p: {pbit};')
                    print(f'  --rom{i}_addr{k}_{j}n: {nbit};')
            i += 1
    return i

def emit_rom_out(out, mux, romlen):
    # assumes emit_rom already called
    print(f'  /* {out} = rom[{mux}]_{out} */')
    split_points = [32, 64, 96, 128, 160, 192, 224, 256, 290]
    resn2 = ''; resp2 = ''
    resp = ''; resn = ''
    for i in range(romlen):
        resp = f'var(--rom{i}_{out}p, {resp})' if resp else f'var(--rom{i}_{out}p)'
        resn = f'var(--rom{i}_{out}n, {resn})' if resn else f'var(--rom{i}_{out}n)'
        if i in split_points:
            print(f'  --{out}_{i}_p: {resp};')
            print(f'  --{out}_{i}_n: {resn};')
            resp2 = f'var(--{out}_{i}_p, {resp2})' if resp2 else f'var(--{out}_{i}_p)'
            resn2 = f'var(--{out}_{i}_n, {resn2})' if resn2 else f'var(--{out}_{i}_n)'
            resp = ''; resn = ''
    print(f'  --{out}p: {resp2};')
    print(f'  --{out}n: {resn2};')

def emit_ram_out(out, mux, ramlen):
    res_p = [''] * 16
    res_n = [''] * 16
    print(f'  /* {out} = t[{mux}] */')
    for i, j in itertools.product(range(ramlen), range(16)):
        print(f'  --{out}{i}_{j}p: var(--{mux}_{i}) var(--t{i}_{j}p);')
        print(f'  --{out}{i}_{j}n: var(--{mux}_{i}) var(--t{i}_{j}n);')
        res_p[j] = f'var(--{out}{i}_{j}p, {res_p[j]})' if res_p[j] else f'var(--{out}{i}_{j}p)'
        res_n[j] = f'var(--{out}{i}_{j}n, {res_n[j]})' if res_n[j] else f'var(--{out}{i}_{j}n)'
    for j in range(16):
        print(f'  --{out}_{j}p: {res_p[j]};')
        print(f'  --{out}_{j}n: {res_n[j]};')


if __name__ == '__main__':
    # arrange toggles in grid, hide by default
    fonts = 'Consolas, "Liberation Mono", Menlo, Courier, monospace'
    print(f'body {{ font-family: {fonts}; margin: auto; width: 340px; margin-top: 32px; }}')
    print('body { display: grid; grid-template-columns: repeat(16, 1fr); }')
    print('input[type="checkbox"] { display: none; }')
    print('#display { grid-column-start: 1; grid-column-end: -1; }')

    # style and position labels
    print('label { padding: 6px 12px; margin-top: 12px }')
    print('label { background-color: white; border: 1px solid; }')
    print('label { position: absolute; left: 50%; transform: translateX(-50%); }')
    print('label { -webkit-user-select: none; user-select: none; }')

    # connect CSS variables to toggle states
    print(f'#display {{ --fp: initial; --fn: ; }}')
    print(f'#f:checked ~ #display {{ --fp: ; --fn: initial; }}')

    for i in range(9):
        print(f'#display {{ --Apc_{i}p: initial; --Apc_{i}n: ; }}')
        print(f'#display {{ --Bpc_{i}p: initial; --Bpc_{i}n: ; }}')
        print(f'#Apc_{i}:checked ~ #display {{ --Apc_{i}p: ; --Apc_{i}n: initial; }}')
        print(f'#Bpc_{i}:checked ~ #display {{ --Bpc_{i}p: ; --Bpc_{i}n: initial; }}')

    tgrid = itertools.product(range(71), range(16))
    for i, j in tgrid:
        print(f'#display {{ --At{i}_{j}p: initial; --At{i}_{j}n: ; }}')
        print(f'#display {{ --Bt{i}_{j}p: initial; --Bt{i}_{j}n: ; }}')
        print(f'#At{i}_{j}:checked ~ #display {{ --At{i}_{j}p: ; --At{i}_{j}n: initial; }}')
        print(f'#Bt{i}_{j}:checked ~ #display {{ --Bt{i}_{j}p: ; --Bt{i}_{j}n: initial; }}')
        if i in range(33):
            print(f'#f:not(:checked) ~ #At{i}_{j} {{ display: inline; }}')
            print(f'#f:checked ~ #Bt{i}_{j} {{ display: inline; }}')

    print('#display {')
    emit_sel('pc', f'Apc', f'Bpc', 'f', 9)
    for i in range(71):
        emit_sel(f't{i}', f'At{i}', f'Bt{i}', 'f', 16)

    # construct CPU components
    romlen = 291
    emit_mux('fmux', 'pc', 9, romlen)
    emit_rom('tetris.qftasm', 'fmux')
    # move to within emit_rom
    outs = ['op_0', 'op_1', 'op_2', 'op_3']
    for k in range(3):
        outs += [f'type{k}_0', f'type{k}_1']
        outs += [f'addr{k}_{j}' for j in range(16)]
    for out in outs:
        emit_rom_out(out, 'fmux', romlen)

    # read operand 0 (loc0)
    emit_mux('a0mux', 'addr0', 7, 71)
    emit_ram_out('a0A', 'a0mux', 71)
    emit_mux('a0Amux', 'a0A', 7, 71)
    emit_ram_out('a0B', 'a0Amux', 71)
    emit_sel('a0C', 'addr0', 'a0A', 'type0_0', 16)
    emit_sel('loc0', 'a0C', 'a0B', 'type0_1', 16)

    # read operand 1 (loc1)
    emit_mux('a1mux', 'addr1', 7, 71)
    emit_ram_out('a1A', 'a1mux', 71)
    emit_mux('a1Amux', 'a1A', 7, 71)
    emit_ram_out('a1B', 'a1Amux', 71)
    emit_sel('a1C', 'addr1', 'a1A', 'type1_0', 16)
    emit_sel('loc1', 'a1C', 'a1B', 'type1_1', 16)

    # read operand 2 (loc2)
    emit_mux('a2mux', 'addr2', 7, 71)
    emit_ram_out('a2A', 'a2mux', 71)
    emit_sel('loc2', 'addr2', 'a2A', 'type2_0', 7)

    # flip loc1 if opcode is SUB
    emit_mux('opmux', 'op', 4, 10, start=4)
    emit_flip('loc1f', 'loc1', 'op_0', 16)
    print(f'  --alu_cin_0p: var(--op_0p);')
    print(f'  --alu_cin_0n: var(--op_0n);')

    # emit ALU, shifter, and bitops
    mov_en = f'var(--op_3n) var(--op_2n) var(--op_1n)'
    emit_mov('mov', 'loc1', 16, mov_en)
    alu_en = f'var(--op_3n) var(--op_2n) var(--op_1p)'
    emit_add('alu', 'loc0', 'loc1f', 'alu_cin', 16, alu_en)
    emit_sll('sll', 'loc0', 'loc1', 'var(--opmux_8)')
    emit_srl('srl', 'loc0', 'loc1', 'var(--opmux_9)')
    emit_bitops('loc0', 'loc1', 16, 'opmux')

    # select output value
    for i in range(16):
        outs = ['alu', 'and', 'or', 'xor', 'ant', 'sll', 'srl']
        outp = f'var(--mov_{i}p)'
        outn = f'var(--mov_{i}n)'
        for out in outs:
            outp = f'var(--{out}_{i}p, {outp})'
            outn = f'var(--{out}_{i}n, {outn})'
        print(f'  --outv_{i}p: {outp};')
        print(f'  --outv_{i}n: {outn};')

    emit_inc('t0_out', 't0', 't0_cin', 16)

    # determine if operand 0 is zero
    print('  /* zero = (loc0 == 0) */')
    for i in range(16):
        resp = f'var(--loc0_{i}n) {resp}' if i > 0 else 'var(--loc0_0n)'
        resn = f'var(--loc0_{i}p, {resn})' if i > 0 else 'var(--loc0_0p)'
    print(f'  --zerop: {resp};')
    print(f'  --zeron: {resn};')

    # set loc2_7 if MLZ/MNZ and condition fails
    print('  /* loc2_7 = (MNZ && zero) || (MLZ && !sign(loc0)) */')
    resp1 = 'var(--op_3n) var(--op_2n) var(--op_1n)'
    resp2 = 'var(--op_0n, var(--loc0_15n)) var(--op_0p, var(--zerop))'
    print(f'  --loc2_7p: {resp1} {resp2};')
    resn1 = 'var(--op_3p, var(--op_2p, var(--op_1p, var(--op_0n, var(--loc0_15p)))))'
    resn2 = 'var(--op_3p, var(--op_2p, var(--op_1p, var(--op_0p, var(--zeron)))))'
    print(f'  --loc2_7n: {resn1} {resn2};')
    emit_mux_pn('wmux', 'loc2', 8, 71)

    # connect CPU output to label display
    for i in range(9):
        print(f'  --Ashow_pc_{i}: var(--fp) {xor_p("Apc", "t0_out", i)} inline;')
        print(f'  --Bshow_pc_{i}: var(--fn) {xor_p("Bpc", "t0_out", i)} inline;')

    # write if wmux, copy from input state if not
    for i in range(71):
        temp = f't{i}' if i != 0 else 't0_out'
        emit_sel(f'show{i}', temp, 'outv', f'wmux_{i}', 16)
        print(f'  /* Ashow{i} = fp && (At{i} ^ show{i}) */')
        for j in range(16):
            diffA = xor_p(f'At{i}', f'show{i}', j)
            diffB = xor_p(f'Bt{i}', f'show{i}', j)
            print(f'  --Ashow{i}_{j}: var(--fp) {diffA} inline;')
            print(f'  --Bshow{i}_{j}: var(--fn) {diffB} inline;')
    print('}')

    print(f'#fl {{ display: inline; }}')
    for i in range(9):
        print(f'#Apcl_{i} {{ display: var(--Ashow_pc_{i}, none); }}')
        print(f'#Bpcl_{i} {{ display: var(--Bshow_pc_{i}, none); }}')

    tgrid = itertools.product(range(71), range(16))
    for i, j in tgrid:
        print(f'#Al{i}_{j} {{ display: var(--Ashow{i}_{j}, none); }}')
        print(f'#Bl{i}_{j} {{ display: var(--Bshow{i}_{j}, none); }}')
