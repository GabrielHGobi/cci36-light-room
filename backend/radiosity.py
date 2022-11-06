import sys, os
from argparse import ArgumentParser
from utils.dae_parser import DAEParser
from utils.radiosity_linear_system import RadiositySystem
from utils.corrections import saturate_color, apply_gama

def parse_arguments():
    rad_parser = ArgumentParser(description='Adds illumination by computing \
        the radiosity on all vertices of a scene on Collada format.')
    rad_parser.add_argument('dae_filename', metavar='file',type=str,
                                help='.dae input file containing the scene')
    rad_parser.add_argument('-o', metavar='output file',type=str, nargs='?',
                                help='name to save the modified .dae file', default='./scene_mod.dae')
    rad_parser.add_argument('lamp_objects_names', metavar='name', type=str, nargs='+',
                                help='objects\' ID of the light objects')
    rad_parser.add_argument('-gama', metavar='gama factor', type=float, nargs='?',
                                help='gama factor for gama correction', default=1.0)
    args = rad_parser.parse_args()
    
    
    if not args.dae_filename.endswith('.dae'):
        print ("Invalid file format: %s. Please provide a .dae file" % args.dae_filename) 
        sys.exit(1)
    else:
        if not os.path.exists(args.dae_filename):
            print ("The file %s does not exist." % args.dae_filename) 
            sys.exit(1)
    if not args.o.endswith('.dae'):
        print ("Invalid file format: %s. Please provide a .dae name for output file." % args.o) 
        sys.exit(1)
    if args.gama < 0 or args.gama > 1:
        print ("Invalid gama value: %.2f. Please provide a gama factor between 0.0 and 1.0." % args.gama) 
        sys.exit(1)
    return args


def main():
    args = parse_arguments()

    # getting all triangles off the scene
    dae_parser = DAEParser(args.dae_filename)
    objects = dae_parser.parse_objects()
    all_triangles = []
    lum_faces = []
    for obj in objects:
        all_triangles += obj.get_triangles()
        for name in args.lamp_objects_names:
            if obj.name == name:
                lum_faces += obj.get_triangles()

    # solving radiosity linear system
    lin_sys = RadiositySystem(all_triangles, lum_faces) 
    lin_sys.solve()

    # putting the results as the color of the faces
    for i, c in enumerate(lin_sys.B):
        color = apply_gama(saturate_color(c), args.gama)
        all_triangles[i].set_color(color)
    
    # writing back to a DAE file
    for obj in objects:
        dae_parser.overwrite_object(obj)
    dae_parser.save_file_to(args.o)
    DAEParser.remove_namespace(args.o)

    # writting it to stdout 
    DAEParser.print_file(args.o)

if __name__ == '__main__':
    main()