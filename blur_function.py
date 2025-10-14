INVALID="INVALID"

def sigma_sum(bottom, top, func):
    """
    Sigma notasjonssum
    """
    if bottom < top:
        _sum=0
        for i in range(bottom, top+1):
            if func:
                _sum+=func(i)
        return _sum
    return INVALID

def find_hue_average(pixel_array, array_len):
    """
    Finner farge basert på relaterte pixler
    *kvadrat

    [
    #, #, #,
    #, #, #,
    #, #, #
    ]
    """
    if not array_len:
        return INVALID
    def f(t,j):
        if t<array_len:
            return pixel_array[t][j]
        return INVALID
    def fr(t):
        return f(t,0)
    def fg(t):
        return f(t,1)
    def fb(t):
        return f(t,2)
    average_r=sigma_sum(0,array_len-1,fr)/array_len
    average_g=sigma_sum(0,array_len-1,fg)/array_len
    average_b=sigma_sum(0,array_len-1,fb)/array_len
    return [int(average_r), int(average_g), int(average_b)]

def get_element(x, y, array, row_len, col_len):
    if row_len-1 < x or x < 0:
        return INVALID
    if col_len-1 < y or y < 0:
        return INVALID
    return array[x+row_len*y]

def set_element(x,y, array, row_len, col_len, c):
    if row_len-1 < x or x < 0:
        return INVALID
    if col_len-1 < y or y < 0:
        return INVALID
    array[x+row_len*y]=c

def set_block(x, y, size, array, row_len, col_len, c):
    if row_len-1 < x+size-1 or x < 0:
        return INVALID
    if col_len-1 < y+size-1 or y < 0:
        return INVALID
    for j in range(y, size):
        for i in range(x, size):
            set_element(i,j,array,row_len, col_len, c)

def coord_from_index(index, row_len ):
    return index%row_len, int(index/row_len)

def find_brush_array(array, row_len, col_len, index, brush_size):
    """
    Finner array som er innenfor *brush*-en ved *index*.
    *brush_size*=1 ==> 1 element fra elementet ved *index*
    NAN --- ved element utenfor *array*
    """
    sub_array = []
    x, y = coord_from_index(index, row_len)
    brush_length=1+2*brush_size
    amount_of_valid=brush_length**2
    for j in range(0, brush_length):
        for i in range(0, brush_length):
            element = get_element(x-brush_size+i, y-brush_size+j, array, row_len, col_len)
            if element != INVALID:
                sub_array.append(element)
            else:
                amount_of_valid-=1

    return sub_array, amount_of_valid
def find_blurred_rgb_value(array, row_len, col_len, index, brush_size):
    """
    Samler relevante pixler, og finner gjennomsnittet.
    """
    brush_array, amount_of_valid = find_brush_array(array, row_len, col_len, index, brush_size)
    return find_hue_average(brush_array, amount_of_valid)

def blur_equal_size(pixel_array, row_len, col_len, brush_size):
    """
    Transformert array. Gjennomsnitt av pixler en *brush_size* distanse
    '#' - *brush*
    [
    #, #, #, ., ., ., .,
    #, #, #, ., ., ., .,
    #, #, #, ., ., ., .,
    ., ., ., ., ., ., .,
    ., ., ., ., ., ., .,
    ., ., ., ., ., ., .,
    ., ., ., ., ., ., .,
    ]
    """
    array_len=row_len*col_len
    transformed_array=[]
    for i in range(0, array_len):
        transformed_array.append(find_blurred_rgb_value(pixel_array, row_len, col_len, i, brush_size))
    return transformed_array

def blur_pixel_array_interpolation(pixel_array, row_len, col_len, size_multiplier):
    """
    Interpolering av *pixel_array*
    """
    transformed_array=[None]*row_len*col_len*size_multiplier**2
    for i in range(0, col_len):
        for j in range(0, row_len):
            set_block(j*size_multiplier, i*size_multiplier, size_multiplier, pixel_array, row_len, col_len, get_element(j, i, pixel_array, row_len, col_len))

sample_pixels1=[
    (1,2,3), (4,5,6), (7,8,9), (2,2,2), (2,2,2), (2,2,2),
    (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2),
    (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2),
    (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2),
    (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2),
    (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2), (2,2,2),
]
sample_pixels2=[
    (2,2,2), (2,2,2),
    (1,3,4), (1,3,4)
]
