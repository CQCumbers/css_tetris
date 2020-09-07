"""
for i in range(71):
    for j in range(16):
        print(f'<input type="checkbox" id="t{i}_{j}">')
    print('')
"""

"""
for i in range(33):
    print(f'<g class="row{i}" transform="translate(0,{i * 20})">')
    print(f'  <text x="5" y="15">{i}</text>')
    for j in range(16):
        print(f'  <rect id="rect{i}_{15-j}" fill="#FFF" x="{20 + j * 20}" y="0" width="20" height="20"></rect>')
    print('</g>')
"""

for i in range(71):
    for j in range(16):
        print(f'<label for="t{i}_{j}" id="l{i}_{j}">WORD {i:02} BIT {j:02}</label>')
    print('')
