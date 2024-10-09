import blenderproc as bproc
import argparse
import numpy as np
import cv2
import os
import sys
import json
import random
from blenderproc.python.loader.ReplicaLoader import load_replica
from blenderproc.python.loader.HavenEnvironmentLoader import set_world_background_hdr_img, get_random_world_background_hdr_img_path_from_haven
from mathutils import Vector, Euler, Matrix
from PIL import Image
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('--output_dir', default="<path-to-output>", help="Path to where the final files, will be saved, could be examples/basics/basic/output")
parser.add_argument('--split', default="<train/val/test>", help="dataset split you want to generate, could be train, val, test, test_unseen")
parser.add_argument('--scene', default="<path-to-replica>", help="Path to where the final files, will be saved, could be examples/basics/basic/output")
args = parser.parse_args()
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
split = args.split

if split == 'train':
    output_split = split
    max_file = 100000
elif split == 'val':
    output_split = split
    max_file = 2000
elif split == 'test':
    output_split = split
    max_file = 2000
elif split == 'test_unseen':
    output_split = split
    max_file = 2000
    
files = os.listdir(os.path.join(args.output_dir, output_split))
width = 5
whole_files = [str(id).zfill(width) for id in range(max_file)]
rest_files = list(set(whole_files) - set(files))
file_id = random.choice(rest_files)
print("file_id:", file_id)
output_dir = os.path.join(args.output_dir, output_split, file_id)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
else:
    print(f"Directory '{output_dir}' already exists. Goodbye the program.")
    sys.exit()

pic_num = 10
roomscale = 10
room_dict = {'office_2': [[-8, -7, -8], [10, 30, 4]], 
            'office_3': [[-7, -20, 0], [11, 17, 5]],
            'office_4':  [[0, -15.0, 0], [35, 15, 12]],
            'room_0': [[0.0, 0.0, 0.0], [55, 30, 5]],
            'room_1': [[-30, -5, -8], [0, 10, 2.5]],
            'room_2': [[10, -12, -12], [40, 6, -7]],
            'hotel_0': [[-25, 3, 0.0], [40, 12, 5]],
            'frl_apartment_0': [[0, -50, -6.25], [40, -30, 4]],
            }

if split == 'test_unseen':
    catId_to_name = {1001: 'air_purifier', 1002: 'apricot', 1003: 'award', 1004: 'ax', 1005: 'bamboo_flute', 1006: 'baseball_bat', 1007: 'baseball_glove', 1008: 'battery', 1009: 'beachball', 1010: 'beauty_blender', 1011: 'bed', 1012: 'binder', 1013: 'blackboard_eraser', 1014: 'blueberry', 1015: 'bookmark', 1016: 'boomerang', 1017: 'bowling_ball', 1018: 'bumbag', 1019: 'cabinet', 1020: 'camel', 1021: 'candied_haws', 1023: 'canned_beverage', 1024: 'chestnut', 1025: 'chinese_cabbage', 1026: 'cigar', 1027: 'clothespin', 1028: 'corkscrew', 1029: 'croquet', 1030: 'ear_phone', 1031: 'electric_cake', 1032: 'electric_pressure_cooker', 1033: 'facial_cleaner', 1035: 'faucet', 1036: 'foot_bath', 1037: 'fork', 1038: 'frisbee', 1039: 'fruit_basket', 1040: 'funnel', 1041: 'glasses', 1042: 'golf', 1043: 'gong', 1044: 'gravy_boat', 1045: 'guitar', 1046: 'hair_curler', 1047: 'headphone', 1048: 'high_heel', 1049: 'hockey', 1050: 'honey_dipper', 1051: 'hulusi', 1053: 'kennel', 1054: 'laptop', 1055: 'life_buoy', 1056: 'lipped', 1057: 'loafer', 1058: 'lollipop', 1059: 'magnet', 1060: 'microphone', 1061: 'microwaveoven', 1063: 'monitor', 1064: 'muffin', 1065: 'nutcracker', 1066: 'ornaments', 1067: 'paintbox', 1068: 'peach_bun', 1069: 'pear', 1070: 'pen', 1071: 'penguin', 1072: 'perfume', 1073: 'phone', 1074: 'piccolo', 1075: 'pigeon', 1076: 'plug', 1077: 'pomelo', 1078: 'pressure_cooker', 1079: 'puffed_food', 1080: 'reptiles', 1081: 'sea_horse', 1082: 'shakuhachi', 1083: 'shower_head', 1084: 'skateboard', 1085: 'slippers', 1086: 'smoke_detector', 1087: 'snare_drum', 1088: 'soccer', 1089: 'soymilk_machine', 1090: 'sweeping_robot', 1091: 'sword_bean', 1092: 'tennis_ball', 1093: 'thermometer', 1094: 'thermos', 1095: 'tobacco_pipe', 1096: 'triangle', 1097: 'tvstand', 1098: 'ukri', 1099: 'wall_lamp', 1100: 'water_chestnut', 1101: 'weaving_basket', 1102: 'wireless_walkie_talkie', 1104: 'wooden_sword', 1105: 'xylophone'}
else:
    catId_to_name = {1: 'aerosol_can', 2: 'alligator', 3: 'almond', 4: 'animal', 5: 'anise', 6: 'antique', 7: 'apple', 8: 'asparagus', 9: 'baby_chinese_cabbage', 10: 'backpack', 11: 'bagel', 12: 'ball', 13: 'balloon', 14: 'bamboo_carving', 15: 'bamboo_shoots', 16: 'banana', 17: 'baseball', 18: 'basketball', 19: 'beer_can', 20: 'bell', 21: 'belt', 22: 'billiards', 23: 'bird', 24: 'birdbath', 25: 'birdhouse', 26: 'biscuit', 27: 'book', 28: 'bottle', 29: 'bottle_opener', 30: 'bowl', 31: 'bowling_pin', 32: 'box', 33: 'boxed_beverage', 34: 'boxing_glove', 35: 'bracelet', 36: 'bread', 37: 'broad_bean', 38: 'broccoli', 39: 'broccolini', 40: 'bronze', 41: 'brush', 42: 'brussels_sprout', 43: 'bucket_noodle', 44: 'bun', 45: 'burrito', 46: 'cabbage', 47: 'cactus', 48: 'cake', 49: 'calculator', 50: 'can', 51: 'candle', 52: 'beet', 53: 'candy_bar', 54: 'carambola', 55: 'carrot', 56: 'castanets', 57: 'cat', 58: 'cauliflower', 59: 'chair', 60: 'charcoal_carving', 61: 'cheese', 62: 'cherry', 63: 'chess', 64: 'chicken_leg', 65: 'chili', 66: 'china', 67: 'chinese_chess', 68: 'chinese_knot', 69: 'chinese_pastry', 70: 'chocolate', 72: 'cigarette', 73: 'cigarette_case', 74: 'clock', 76: 'coconut', 77: 'coin', 79: 'conch', 80: 'coral', 81: 'corn_skin', 82:'corn', 83: 'crab', 84: 'crayon', 85: 'cricket', 86: 'cucumber', 87: 'cup', 88: 'cushion', 89: 'date_fruit', 90: 'dental_carving', 91: 'desk_lamp', 92: 'dice', 93: 'dinosaur', 94: 'dish', 95: 'dishtowel', 96: 'dog', 97: 'dog_food', 98: 'doll', 99: 'donut', 100: 'drawing', 101: 'drum', 102: 'drumstick', 103: 'duct_tape', 104: 'dumbbell', 105: 'dumpling', 106: 'durian', 107: 'dustbin', 108: 'earplug', 109: 'edamame', 110: 'egg', 111: 'egg_roll', 112: 'egg_tart', 113: 'eggplant', 114: 'electric_clippers', 115: 'electric_toothbrush', 116: 'eleocharis_dulcis', 118: 'facial_cream', 119: 'facial_tissue_holder', 120: 'fan', 121: 'fig', 122: 'fire_extinguisher', 123: 'fish', 124: 'flash_light', 125: 'flower_pot', 126: 'flute', 127: 'football', 128: 'fountain_pen', 129: 'french_chips', 130: 'garage_kit', 133: 'glasses_case', 134: 'gloves', 135: 'gourd', 136: 'grass_roller', 137: 'green_bean_cake', 138: 'guacamole', 139: 'gumbo', 140: 'gundam_model', 141: 'hair_dryer', 142: 'hairpin', 143: 'hamburger', 144: 'hami_melon', 145: 'hammer', 146: 'hand_cream', 147: 'hand_drum', 148: 'handbag', 149: 'handball', 150: 'handstamp', 151: 'hat', 152: 'haw_thorn', 154: 'headband', 155: 'helmet', 156: 'horse', 157: 'hot_dog', 158: 'house', 159: 'household_blood_glucose_meter', 160: 'humidifier', 163: 'insole', 167: 'joystick', 168: 'kettle', 169: 'keyboard', 170: 'kidney_beans', 171: 'kite', 172: 'kiwifruit', 173: 'knife', 174: 'lacquerware', 175: 'lantern', 176: 'laundry_detergent', 177: 'lego', 178: 'lemon', 179: 'lettuce', 180: 'light', 181: 'lint_remover', 182: 'lipstick', 183: 'litchi', 184: 'lizard', 185: 'longan', 186: 'loquat', 187: 'lotus_root', 188: 'macaron', 190: 'mangosteen', 191: 'maracas', 192: 'mask', 193: 'matchbox', 194: 'medicine_bottle', 195: 'milk', 196: 'mooncake', 197: 'mouse', 198: 'mousepad', 199: 'mushroom', 200: 'nailfile', 201: 'nesting_dolls', 202: 'nipple', 203: 'nuclear_carving', 204: 'onion', 205: 'orange', 206: 'ornament', 207: 'oyster', 208: 'package', 209: 'pad', 210: 'padlock', 211: 'paintbrush', 212: 'pan', 213: 'pancake', 214: 'paper_knife', 215: 'passion_fruit', 216: 'pastry', 217: 'peach', 218: 'peanut', 219: 'persimmon', 220: 'phone_case', 221: 'photo_frame', 222: 'picnic_basket', 223: 'pie', 224: 'pillow', 225: 'pineapple', 226: 'pinecone', 227: 'pingpong', 228: 'pistachio', 229: 'pitaya', 230: 'pizza', 231: 'plant', 232: 'pocket_watch', 234: 'poker', 235: 'pomegranate', 236: 'popcorn', 239: 'pottery', 240: 'power_strip', 241: 'projector', 242: 'prune', 243: 'puff', 244: 'pumpkin', 245: 'puppet', 246: 'radio', 247: 'radish', 248: 'razor', 249: 'red_cabbage', 250: 'red_jujube', 251: 'red_wine_glass', 252: 'remote_control', 254: 'ricecooker', 255: 'root_carving', 256: 'rubik_cube', 257: 'sandwich', 258: 'sausage', 259: 'scissor', 260: 'screwdriver', 261: 'set_top_box', 262: 'shampoo', 263: 'shaomai', 264: 'shoe', 265: 'shrimp', 266: 'soap', 267: 'sofa', 268: 'softball', 269: 'spanner', 270: 'speaker', 271: 'spice_mill', 272: 'squash', 273: 'starfish', 274: 'steamed_bun', 275: 'steamed_twisted_roll', 276: 'stone_carving', 277: 'stool', 278: 'straw', 279: 'strawberry', 280: 'suitcase', 281: 'sushi', 282: 'sweet_potato', 283: 'table', 284: 'table_tennis_bat', 285: 'tamarind', 286: 'tambourine', 287: 'tang_sancai', 288: 'tank', 289: 'tape_measure', 290: 'taro', 291: 'teacup', 292: 'teakettle', 293: 'teapot', 294: 'teddy_bear', 295: 'thermos_bottle', 296: 'thimble', 297: 'timer', 298: 'tissue', 299: 'tomato', 300: 'tongs', 301: 'toolbox', 302: 'tooth_brush', 303: 'tooth_paste', 304: 'toothpick_box', 305: 'toy_animals', 306: 'toy_boat', 307: 'toy_bus', 308: 'toy_car', 309: 'toy_gun', 310: 'toy_motorcycle', 311: 'toy_plane', 312: 'toy_plant', 313: 'toy_train', 314: 'toy_truck', 315: 'toys', 316: 'tray', 317: 'turtle', 319: 'umbrella', 320: 'vase', 321: 'vine_ball', 322: 'volleyball', 323: 'waffle', 324: 'wallet', 325: 'walnut', 326: 'watch', 327: 'water_gun', 328: 'watering_can', 329: 'watermelon', 330: 'wenta_walnut', 331: 'whistle', 334: 'wooden_ball', 335: 'wooden_spoon', 336: 'woodfish', 337: 'world_currency', 338: 'yam', 339: 'zongzi'}

if split == 'train':
    room_list = ['office_2', 'room_0', 'hotel_0', 'frl_apartment_0']
elif split == 'val':
    room_list = ['office_4', 'room_2']
else:
    room_list = ['office_3', 'room_1']
name_to_catId = {value:key for key,value in catId_to_name.items()}

room_name = random.choice(room_list)
# print(room_name)
# print("room_name:", room_name)

def create(room_name):  
    # global location_list
    bproc.init() 
    bproc.renderer.set_light_bounces(diffuse_bounces=200, glossy_bounces=200, max_bounces=200,
                                  transmission_bounces=200, transparent_max_bounces=200)
    room = load_replica(args.scene, room_name, use_smooth_shading = True)[0]
    size = room.get_bound_box()
    size_x = max(abs(size[:, 0]))
    size_y = max(abs(size[:, 1]))
    size_z = max(abs(size[:, 2]))
    print(size_x, size_y, size_z)
    room.set_scale([roomscale, roomscale, roomscale])
    
    model_objects = "<path-to-your-objectmesh>"
    model_num = random.choice(list(range(4,7)))
    models = []
    cates = os.listdir(os.path.join(model_objects, split))
    for cate in sorted(cates):
        objects = os.listdir(os.path.join(model_objects, split, cate))
        for obj in objects:
            if os.path.exists(os.path.join(model_objects, split, cate, obj, 'Scan/Scan_norm.obj')):
                models.append(os.path.join(model_objects, split, cate, obj, 'Scan/Scan_norm.obj'))
    print(len(models))
    objs_path = random.choices(models, k = model_num)

    objs = []
    for obj_id in range(len(objs_path)):
        obj_path = objs_path[obj_id]
        scale_path = objs_path[obj_id].replace('Scan_norm.obj', 'scale.json')
        with open(scale_path, 'r') as f:
            obj_scale = json.load(f)
        print(obj_path, obj_scale)
        obj = bproc.loader.load_obj(obj_path)[0]
        cate_id = name_to_catId[obj_path.split('/')[-4]]
        obj.set_cp("category_id", cate_id)
        obj.set_cp("instance_id", obj_id + 1)
        obj.set_cp("obj_scale", obj_scale)
        objs.append(obj)

    light = bproc.types.Light()
    '''点光源的设置'''
    light_class = 'POINT'
    light.set_energy(random.uniform(500, 700)*roomscale)
    if room_name == 'room_0':
        light.set_energy(random.uniform(550, 650)*roomscale)
    if room_name == 'room_1':
        light.set_energy(random.uniform(400, 500)*roomscale)
    if room_name == 'hotel_0':
        light.set_energy(random.uniform(1100, 1300)*roomscale)
    if room_name == 'office_2':
        light.set_energy(random.uniform(1400, 1600)*roomscale)
    if room_name == 'office_3':
        light.set_energy(random.uniform(550, 650)*roomscale)
    light.set_type(light_class)
    center_init = np.mean(np.array([room_dict[room_name][0], room_dict[room_name][1]]), axis = 0)
    center_init[2] = room_dict[room_name][1][2]
    light.set_location(bproc.sampler.shell(
        center = center_init,
        radius_min=0.4*roomscale,
        radius_max=0.6*roomscale,
        elevation_min=0,
        elevation_max=1
    ))
    
    sizes = []
    max_size = 0
    for obj in objs:
        obj_scale = obj.get_cp("obj_scale")
        size = obj.get_bound_box()
        size_x = max(abs(size[:, 0]))
        size_y = max(abs(size[:, 1]))
        size_z = max(abs(size[:, 2]))
        if obj_scale > max_size:
            max_size = obj_scale
        real_size = [size_x, size_y, size_z, obj_scale * 0.02]
        sizes.append(real_size)
        # 前者表示归一化模型的scale，后者表示模型从[0,1]^3单位空间中的放缩
        # obj.set_scale([0.2, 0.2, 0.2])
        obj.set_scale([obj_scale * 0.02, obj_scale * 0.02, obj_scale * 0.02])
        # # print(obj.get_bound_box())
        obj.enable_rigidbody(active=True)
    print('max_size:', max_size)
    print('sizes:', sizes)
    bproc.camera.set_intrinsics_from_K_matrix(
        [[577.5, 0.0, 319.5],
        [0.0, 577.5, 239.5],
        [0.0, 0.0, 1.0]], 640, 480
    )
    
    init_pose = np.random.uniform(np.array(room_dict[room_name][0]), np.array(room_dict[room_name][1]))
    init_pose[2] = room_dict[room_name][1][2]
    def sample_pose(obj: bproc.types.MeshObject):
        location = init_pose + np.random.uniform([-0.8, -0.8, -2], [0.8, 0.8, 2])
        if location[0] <= room_dict[room_name][0][0]:
            location[0] = room_dict[room_name][0][0]
        if location[0] >=room_dict[room_name][1][0]:
            location[0] = room_dict[room_name][1][0]
        if location[1] <= room_dict[room_name][0][1]:
            location[1] = room_dict[room_name][0][1]
        if location[1] >= room_dict[room_name][1][1]:
            location[1] = room_dict[room_name][1][1] 
        obj.set_location(location)
        print(catId_to_name[obj.get_cp("category_id")], obj.get_location())
        obj.set_rotation_euler(bproc.sampler.uniformSO3())

    
    # Sample the poses of all spheres above the ground without any collisions in-between
    bproc.object.sample_poses(
        objs,
        sample_pose_func=sample_pose,
        max_tries = 10
    )
    
    print("Complete sampling the poses")
    # The ground should only act as an obstacle and is therefore marked passive.
    # To let the spheres fall into the valleys of the ground, make the collision shape MESH instead of CONVEX_HULL.
    room.enable_rigidbody(active=False, collision_shape="MESH")
    # Run the simulation and fix the poses of the spheres at the end
    bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=0.1, max_simulation_time=5, check_object_interval=1, substeps_per_frame = 1)
    print("Complete!")
    poi = bproc.object.compute_poi(objs)
    cam2world_matrixs = []
    camera_scale = max_size/50/1.5
    print("camera_scale:", 0.8*roomscale*camera_scale, 1*roomscale*camera_scale)
    for i in range(pic_num):
        select = random.choice(objs)
        center = np.array(select.blender_obj.location)
        location = bproc.sampler.shell(
                center = poi,
                radius_min=0.8*roomscale*camera_scale,
                radius_max=1*roomscale*camera_scale,
                elevation_min=30,
                elevation_max=90
        ) 
        if location[0] <= room_dict[room_name][0][0]:
            location[0] = room_dict[room_name][0][0]
        if location[0] >=room_dict[room_name][1][0]:
            location[0] = room_dict[room_name][1][0]
        if location[1] <= room_dict[room_name][0][1]:
            location[1] = room_dict[room_name][0][1]
        if location[1] >= room_dict[room_name][1][1]:
            location[1] = room_dict[room_name][1][1] 
        if location[2] >= room_dict[room_name][1][2]:
            location[2] = room_dict[room_name][1][2] 
        print("Camera_loc:", location)
        if location[2] < room_dict[room_name][0][2]-20 and os.path.exists(output_dir):
            os.rmdir(output_dir)
            print(output_dir)
            return
                
        # Compute rotation based on vector going from location towards poi
        rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=np.random.uniform(-0.0, 0.0))
        # Add homog cam pose based on location an rotation
        cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
        bproc.camera.add_camera_pose(cam2world_matrix)
        cam2world_matrixs.append(cam2world_matrix)
        
    # 测试物体的位置
    gt_data = dict()
    category_ids = []
    instance_ids = []
    locations = []
    rotation_mats = []
    scales = []
    local2world_mats = []
    
    error_num = 0
    for obj in objs:
        category_id = obj.get_cp("category_id")
        instance_id = obj.get_cp("instance_id")
        obj_scale = obj.get_cp("obj_scale")
        location = obj.get_location()
        rotation_mat = obj.get_rotation_mat()
        scale = obj.get_scale()
        local2world_mat = obj.get_local2world_mat()
        category_ids.append(category_id)
        instance_ids.append(instance_id)
        locations.append(location)
        rotation_mats.append(rotation_mat)
        scales.append(scale)
        local2world_mats.append(local2world_mat)
        if location[2] < room_dict[room_name][0][2]-20:
            error_num += 1
    if error_num >= 3 and os.path.exists(output_dir):
        os.rmdir(output_dir)
        print(output_dir)
        return

    gt_data["category_id"] = category_ids
    gt_data["instance_id"] = instance_ids
    gt_data["location"] = locations
    gt_data["rotation_mat"] = rotation_mats
    gt_data["scale"] = scales
    gt_data["size"] = sizes
    gt_data["local2world_mat"] = local2world_mats
    gt_data["cam2world_matrix"] = cam2world_matrixs

    gt_file = os.path.join(output_dir, 'gt.pkl')
    with open(gt_file, "wb") as f:
        pickle.dump(gt_data, f)
    f.close()
    
    bproc.renderer.enable_segmentation_output(map_by= "instance_id", default_values={'instance_id': 255})
    bproc.renderer.enable_depth_output(activate_antialiasing=False)
    data = bproc.renderer.render()
    nocs_data = bproc.renderer.render_nocs()
    data.update(nocs_data)   
    
    for item in data:
        for id in range(len(data[item])):
            array = data['instance_id_segmaps'][id]
            room_area = (array == 255).sum()
            background = (array == 0).sum()
            object_area = 480*640 - room_area - background
            if background > 0 or object_area < 1000 or room_area == 0:
                continue
            meta_file = os.path.join(output_dir, str(id).zfill(4)+'_meta.txt')
            with open(meta_file, 'w', encoding='utf-8') as f:
                for obj_id in range(len(objs_path)):
                    cate, obj = objs_path[obj_id].split('/')[-4:-2]
                    cate_id = name_to_catId[cate]
                    result2txt = ' '.join([str(obj_id+1), str(cate_id), cate, obj]) + '\n'
                    f.write(result2txt)
            f.close()
            if item in ['colors', 'depth', 'instance_id_segmaps', 'nocs']:
                array = np.array(data[item][id])
                if item == 'colors':
                    array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
                    output_file = os.path.join(output_dir, str(id).zfill(4)+'_color.png')
                    cv2.imwrite(output_file, array)
                    print(room_area, background, object_area)
                elif item == 'depth':
                    output_file = os.path.join(output_dir, str(id).zfill(4)+'_depth.png')
                    array = array*10000
                    print('far:', np.max(np.max(array)))
                    array0 = array//(256*256)
                    array1 = (array//256)%256
                    array2 = array%256
                    array3 = np.ones(array.shape)
                    array0 = np.expand_dims(array0, 2)
                    array1 = np.expand_dims(array1, 2)
                    array2 = np.expand_dims(array2, 2)
                    array3 = np.expand_dims(array3, 2)
                    new = np.concatenate([array0, array1, array2, array3*255],axis = 2) 
                    cv2.imwrite(output_file, new)
                elif item == 'instance_id_segmaps':
                    output_file = os.path.join(output_dir, str(id).zfill(4)+'_mask.png')
                    cv2.imwrite(output_file, array)
                elif item == 'nocs':
                    array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
                    output_file = os.path.join(output_dir, str(id).zfill(4)+'_coord.png')
                    array *= 255
                    array[np.array(data['instance_id_segmaps'][id]) == 255] = np.array([255, 255, 255])
                    cv2.imwrite(output_file, array)
            else:
                continue
             

create(room_name)
