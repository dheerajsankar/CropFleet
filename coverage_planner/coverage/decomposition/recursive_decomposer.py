from shapely.ops import split
from coverage_planner.coverage.decomposition.split_generator import split_generator,split_validation
from coverage_planner.coverage.decomposition.concavity_detector import detect_concave_vertices


def recursive_decompose(polygon, original_area=None):
    if  original_area is None:
        original_area = polygon.area
    if polygon.area <= original_area * 0.005:
        return [polygon]
    
    concave_points = detect_concave_vertices(polygon)
    decomposed_cells  = []
    
    if len(concave_points) == 0:
        return [polygon]
    
    else:
        hor_split_lines, ver_split_lines = split_generator(polygon, concave_points)
        valid_hor_splits, valid_ver_splits = split_validation(polygon, hor_split_lines, ver_split_lines)
        all_splits = valid_hor_splits + valid_ver_splits
        if all_splits == []:
            return [polygon]
        else:
            valid_candidates =  []
            for  split_line in all_splits:
                split_result = split(polygon, split_line)
                valid_split = True
                for child in split_result.geoms:
                    minx, miny, maxx, maxy = child.bounds
                    width = maxx - minx
                    height = maxy - miny
                    if width  ==  0 or height == 0:
                        valid_split = False
                        break
                    aspect_ratio = max(width, height) / min(width, height)
                    if aspect_ratio > 10:
                        valid_split = False
                        break
                if valid_split:
                    valid_candidates.append(split_line)
            if not valid_candidates:
                return [polygon]
            chosen_split= max(valid_candidates, key=lambda line: line.length)
            split_result = split(polygon, chosen_split)
            for child in split_result.geoms:
                cells = recursive_decompose(child, original_area)
                decomposed_cells.extend(cells)
                

    return decomposed_cells
            






        


    



    





