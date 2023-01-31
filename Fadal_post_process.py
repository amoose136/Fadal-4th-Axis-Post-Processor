import argparse, glob
from pdb import set_trace as br
from copy import copy
from pathlib import Path, PurePath

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Post process code generated with HSMWorks/Fusion360 using the 'Haas with A axis' post so it's usable with a Fadal with A axis")
    parser.add_argument('files',metavar='foo.nc',type=str,nargs='+',help='gcode files to process (1 or more args)')
    parser.add_argument('--fnames',type=str,nargs='+',action='store',help='Choose the name of the output')
    parser.add_argument('--directory',type=str,nargs='+',dest='dir',action='store',help='Output gcode in directory specified instead of next to input files.')
    args=parser.parse_args()
    first_line_corrected=False
    o_filenames=[]
    i_filenames=copy(args.files) #must not be none
    # Handle the star operator (Windows is not as good as shell in this regard) as an input. IE resolve to all the nc files in the directory
    if len(i_filenames)==1 and PurePath(i_filenames[0]).name=='*.nc':
        i_filenames=glob.glob(i_filenames[0])
    if args.fnames is not None:
        if len(args.fnames)!=len(args.files):
            print("Error: number of output names must equal number of input names")
            print("\tNumber of inputs:\t"+str(len(args.files)))
            print("\tNumber of outputs:\t"+str(len(args.fnames)))
            exit()
        else:
            o_filenames=args.fnames
            for i,name in enumerate(o_filenames):
                o_filenames[i]=Path(name)
    else:
        for i,name in enumerate(i_filenames):
            i_filenames[i]=Path(name)
        o_filenames=copy(i_filenames)
    directory='.' #IE current working directory
    if args.dir is not None:
        directory=Path(args.dir[0])
    for i,path in enumerate(o_filenames):
        if args.fnames is not None:
             o_filenames[i]=PurePath.joinpath(Path(directory),path.name)
        else:
            o_filenames[i]=PurePath.joinpath(Path(directory),path.name[:-3]+"_fd.nc")
    for f_index,fin in enumerate(i_filenames):
        print("Processing "+str(fin)+" -> "+str(o_filenames[f_index]))
        with fin.open() as f:
            with o_filenames[f_index].open(mode='w') as fout:
                input = f.readlines()
                input = [i.strip() for i in input]
                length=len(input)
                print(length)
                prog_len=0
                old_coord=0
                for number, line in enumerate(input):
                    if number>length-13:
                        break
                    words = line.split()
                    if number==length-14:
                        prog_len=int(words[0][1:])
                    for i,word in enumerate(words):
                        if word == "N10" and first_line_corrected==False:
                            fout.write("N10 G0G17G40G49G70G80G90G98")
                            words=[]
                            first_line_corrected=True
                            break
                        if word[0]=='A':
                            coord=float(word[1:])
                            # Modulus makes it so the sign is only ever between 0 and 360
                            if coord>old_coord:
                                words[i]='A'+f"{coord%360:.3f}" #if the new coordinate is larger than the old coordinate, the sign of the a coordinate should be positive
                            else:
                                words[i]='A-'+f"{coord%360:.3f}" #if the new coordinate is less than the old coordinate, the sign of the a coordinate should be negative
                            old_coord=coord
                        if word=='M11':
                            words[i]='M61'
                        if word=='M10':
                            words[i]='M60'
                        if word=='F500.':
                            words[i]='F300.'
                        if word=='G54': #fixture offsets
                            words[i]='E1'
                        if word=="G53":  #use machine coordinate system
                            words.pop(i)
                    line = " ".join(words)
                    if number > 1:
                        fout.write(line+"\n")
                fout.write("\n")
                fout.write("N"+str(prog_len+5)+" M5 M9\n")
                fout.write("N"+str(prog_len+15)+" G0 Z0 G49\n")
                fout.write("N"+str(prog_len+20)+" G0 X0 Y0 E0\n")
                fout.write("N"+str(prog_len+25)+" M2\n")
                fout.write("\n")
                fout.write("%\n")
                fout.write("\n")