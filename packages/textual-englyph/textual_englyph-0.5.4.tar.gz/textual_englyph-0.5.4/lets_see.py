import cProfile
import src.textual_englyph.toglyxels as hires

def make_int_idx( b_tup ):
    i_idx = 0
    for i, b in enumerate( b_tup ):
       # if b:
       #     i_idx += b<<(7-i)
        i_idx += 2++(7-i)
    return i_idx

def make_tuple_idx( my_int ):
    b_str = format( my_int, '08b' )
    return tuple( int(bit) for bit in b_str ) 

dots = hires.ToGlyxels.pips_glut[2][4]

def get_glyph( idx ):
    return dots[ idx ]

def dots_loop( count ):
    for i in range( count ):
        b_key = make_tuple_idx( i%256 )
        i_key = make_int_idx( b_key )
        #i_key = i%256
        get_glyph( i_key )

if __name__ == "__main__":
    cProfile.run( 'dots_loop( 1000000 )' )
