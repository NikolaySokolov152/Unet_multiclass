from model import *
from data import *

# import json
import skimage.io as io
import numpy as np
from splitImages import *
from AGCWD import *


#rgb
any                 = [192, 192, 192]   #light-gray
borders             = [0,0,255]         #blue
mitochondria        = [0,255,0]         #green
mitochondria_borders= [255,0,255]       #violet
PSD                 = [192,192,64]      #yellow
axon                = [192,128,64]      #yellow
vesicles            = [255,0,0]         #read


def test(model_name, save_dir, num_class = 1, size_test_train = 12):
   
    model = keras.models.load_model(model_name, compile = False)
    name_list = []
    testGene = testGenerator(test_path = "data/test", name_list = name_list, save_dir = save_dir,\
                              num_image = size_test_train, flag_multi_class = True)

    results = model.predict_generator(testGene, size_test_train, verbose=1)
    saveResultMask(save_dir, results, name_list, num_class=num_class)
    #saveResult("data/result", results, name_list, trust_percentage = 0.95, flag_multi_class = True, num_class = num_class)

def test_one_img(model_name, save_dir, img_name, filepath = "data/test", num_class = 1):

    model = keras.models.load_model(model_name, compile = False)

    img = io.imread(os.path.join(filepath, img_name))
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    img = to_0_1_format_img(img)

    img = trans.resize(img, (256,256))
    img = np.reshape(img, (1,) + img.shape)

    #io.imsave(os.path.join(save_dir, img_name), img[0])

    results = model.predict(x = img, batch_size = 1, verbose = 1)

    results = [trans.resize(results[0], (768,1024,num_class))]

    saveResultMask(save_dir, results, [img_name], num_class=num_class)
    #saveResult("data/result", results, name_list, trust_percentage = 0.95, flag_multi_class = True, num_class = num_class)

def tiled_generator(tiled_arr):
    for img in tiled_arr:
        #img = np.reshape(img, img.shape + (1,))
        img = np.reshape(img, (1,) + img.shape)
        yield img

def glit_mask(tiled_masks, num_class, out_size, tile_info, overlap = 64):
    masks = []
    for i_class in range(num_class):
        pic = tiled_masks[:,:,:,i_class]
        i_mask = glit_image(pic, out_size, tile_info, overlap)
        #print(result_class.shape)
        masks.append(i_mask)

    #print(masks[0].shape)
    union_arr = np.zeros(out_size + (num_class,), np.uint8)
    for i_class in range(num_class):
        union_arr[:,:,i_class] = masks[i_class]
    #print(union_arr.shape)

    return np.reshape(union_arr, (1,) + union_arr.shape)

#main tailing function
def test_tiled(model_name, num_class, save_mask_dir,  filenames, filepath = "data/test", size = 256, overlap = 64, save_dir = None, unique_area = 0):
    
    model = keras.models.load_model(model_name, compile = False)
    
    for i,img_name in enumerate(filenames):
        print(i+1, "image is ", len(filenames))

        img = io.imread(os.path.join(filepath, img_name))
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #img = agcwd(img)
        img = to_0_1_format_img(img)

        tiled_name = img_name.split('.')[0]
        tiled_arr, tile_info = split_image(img, tiled_name, save_dir, size, overlap, unique_area)
    
    
        img_generator = tiled_generator(tiled_arr)
    
        results = model.predict(img_generator, batch_size = 1, verbose = 1)
        #print("results", results.shape)
    
        res_img = glit_mask(results, num_class, img.shape, tile_info, overlap)
        #print("glit_mask", res_img.shape)
    
        saveResultMask(save_mask_dir, res_img, [img_name], num_class = num_class)


def test_models():
    data = "2022_11_16"

    CNN_name = [
                #"real_data_256_tiny_unet_5_num_class_27_slices",
                #"real_data_256_tiny_unet_5_num_class_27_slices_v3",
                "real_data_256_unet_6_num_class_27_slices_no_noise_no_zoom_v2",
                #"real_data_256_unet_6_num_class_27_slices_no_noise_no_zoom_v3_new_gen"            
               ]
     
    list_CNN_name = []
     
    for name in CNN_name:
        change_name = "обучение " + data + "/" + name + ".hdf5"  
        list_CNN_name.append(change_name)

    list_CNN_num_class = [
                          #5,
                          #5,
                          #6,
                          #6
                          ]

    result_CNN_dir = []
    
    for i in range(len(CNN_name)):
        save_name = "data/result_all_slices/" + data + "/" + str(list_CNN_num_class[i]) + "_class/" + CNN_name[i]
        result_CNN_dir.append(save_name)

    overlap_list = [64]

    for i in range(len(list_CNN_num_class)):
        print("predict ", list_CNN_name[i], " model")
        for overlap in overlap_list:
            print("     predict tiled with overlap: ", overlap)
            test_tiled(model_name = list_CNN_name[i],
                       num_class = list_CNN_num_class[i],
                       save_mask_dir = result_CNN_dir[i] + "_" + str(overlap),
                       overlap = overlap,
                       filenames = ["testing0000.png"])

        print("     predict one img")
        test_one_img(model_name= list_CNN_name[i],
                save_dir= result_CNN_dir[i]+"_image_one",
                img_name= "testing0000.png",
                num_class = list_CNN_num_class[i])

def test_models_all_dir():
    data = "2022_11_16"

    CNN_name = [
                #"real_data_256_tiny_unet_5_num_class_27_slices",
                #"real_data_256_tiny_unet_5_num_class_27_slices_v3",
                "real_data_256_unet_6_num_class_27_slices_no_noise_no_zoom_v2",
                #"real_data_256_unet_6_num_class_27_slices_no_noise_no_zoom_v3_new_gen"            
               ]
     
    list_CNN_name = []
     
    for name in CNN_name:
        change_name = "обучение " + data + "/" + name + ".hdf5"  
        list_CNN_name.append(change_name)

    list_CNN_num_class = [
                          #5,
                          #5,
                          6,
                          #6
                          ]

    result_CNN_dir = []
    
    for i in range(len(CNN_name)):
        save_name = "data/result_all_slices/" + data + "/" + str(list_CNN_num_class[i]) + "_class/" + CNN_name[i]
        result_CNN_dir.append(save_name)

    overlap_list = [64]

    filepath =  "data/train slices"
    list_test_img_dir = os.listdir(os.path.join(filepath))
    list_test_img_dir = [name for name in list_test_img_dir if name.endswith(".png") ]

    for i in range(len(list_CNN_num_class)):
        print("predict ", list_CNN_name[i], " model")
        for overlap in overlap_list:
            print("     predict tiled with overlap: ", overlap)
            test_tiled(model_name = list_CNN_name[i],
                       num_class = list_CNN_num_class[i],
                       save_mask_dir = result_CNN_dir[i] + "_" + str(overlap),
                       overlap = overlap,
                       filepath = filepath,
                       filenames = list_test_img_dir) #, save_dir= "data/split test/")
"""
        print("     predict one img")
        test_one_img(model_name= list_CNN_name[i],
                save_dir= result_CNN_dir[i]+"_image_one",
                img_name= "testing0000.png",
                num_class = list_CNN_num_class[i])
"""

if __name__ == "__main__":
    #test_models()
    test_models_all_dir()






