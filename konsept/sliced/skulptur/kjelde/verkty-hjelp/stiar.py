import glob, os
SP = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
for f in glob.glob(f'{SP}/verkty/*.ts'):
    s = open(f, encoding='utf8').read()
    o = s
    s = s.replace('from "/home/user/slicer.iverfinne.no/', 'from "../slicer/')
    s = s.replace('/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe', SP)
    s = s.replace('/home/user/slicer.iverfinne.no', f'{SP}/slicer')
    if s != o:
        open(f, 'w', encoding='utf8').write(s)
        print('retta', os.path.basename(f))
