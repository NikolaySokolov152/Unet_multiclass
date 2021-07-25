import numpy as np
import cv2
import copy
import os
import json

import skimage.io as io

import sklearn.metrics


def to_0_255_format_img(in_img):
    max_val = in_img[:,:].max()
    if max_val <= 1:
       out_img = np.round(in_img * 255)
       return out_img.astype(np.uint8)
    else:
        return in_img

def viewImage(image, name_of_window):
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def jaccard(x,y):
  x = np.asarray(x, np.bool) # Not necessary, if you keep your data
  y = np.asarray(y, np.bool) # in a boolean array already!
  return np.double(np.bitwise_and(x, y).sum()) / np.double(np.bitwise_or(x, y).sum())

def dice(y_true, y_pred):
	y_true = np.asarray(y_true, np.bool)  # Not necessary, if you keep your data
	y_pred = np.asarray(y_pred, np.bool)  # in a boolean array already!
	intersection = np.double(np.bitwise_and(y_true, y_pred).sum())
	#print(2 * intersection, len(y_true) + len(y_pred), 1024*768)
	#print(intersection)
	return (2. * intersection) / ((y_true.sum()) + (y_pred.sum()))
	
def RI(y_true, y_pred):
	y_true = np.asarray(y_true, np.bool)
	y_pred = np.asarray(y_pred, np.bool)
	
	y_true = np.asarray(y_true, np.int32)
	y_pred = np.asarray(y_pred, np.int32)
	
	#print(y_true.sum())
	#print(y_pred.sum())
		
	TN, FP, FN, TP = sklearn.metrics.confusion_matrix(y_true, y_pred).ravel()
	
	#print (TN, FP, FN, TP)
	
	n = len(y_true)
	
	a = 0.5 *(TP*(TP-1)+FP*(FP-1)+TN*(TN-1)+FN*(FN-1))
	
	b = 0.5 *((TP+FN)**2 + (TN+FP)**2 - (TP**2+ TN**2+ FP**2+ FN**2))
	
	#print(TP, TP**2, TN, TN**2, FP, FP**2, FN, FN**2)
	
	c = 0.5 *((TP+FP)**2 + (TN+FN)**2 - (TP**2+ TN**2+ FP**2+ FN**2))
	
	d = n*(n-1)/2 - (a+b+c)
		
	RI = (a+b)/(a+b+c+d)
		
	return RI

def Accuracy(y_true, y_pred):

	y_true = np.asarray(y_true, np.bool)
	y_pred = np.asarray(y_pred, np.bool)
	
	y_true = np.asarray(y_true, np.int32)
	y_pred = np.asarray(y_pred, np.int32)
	
	#print(y_true.sum())
	#print(y_pred.sum())
		
	TN, FP, FN, TP = sklearn.metrics.confusion_matrix(y_true, y_pred).ravel()
		
	Accuracy = float(TN + TP)/(TN + TP+ FN + FP)
		
	return Accuracy
	
def Precition(y_true, y_pred):

	y_true = np.asarray(y_true, np.bool)
	y_pred = np.asarray(y_pred, np.bool)
	
	y_true = np.asarray(y_true, np.int32)
	y_pred = np.asarray(y_pred, np.int32)
			
	TN, FP, FN, TP = sklearn.metrics.confusion_matrix(y_true, y_pred).ravel()
		
	return float(TP)/(TP+FP)
	
def Recall(y_true, y_pred):

	y_true = np.asarray(y_true, np.bool)
	y_pred = np.asarray(y_pred, np.bool)
	
	y_true = np.asarray(y_true, np.int32)
	y_pred = np.asarray(y_pred, np.int32)
			
	TN, FP, FN, TP = sklearn.metrics.confusion_matrix(y_true, y_pred).ravel()
				
	return float(TP)/(TP+FN)
	
def Fscore(y_true, y_pred):

	y_true = np.asarray(y_true, np.bool)
	y_pred = np.asarray(y_pred, np.bool)
	
	y_true = np.asarray(y_true, np.int32)
	y_pred = np.asarray(y_pred, np.int32)
	
	#print(y_true.sum())
	#print(y_pred.sum())
	precition = Precition(y_true, y_pred)	
	recall = Recall(y_true, y_pred)	
	
	return (2*precition*recall)/(precition+recall)

mask_name_label_list = ["mitochondria", "PSD", "vesicles", "axon", "boundaries", "mitochondrial boundaries"]

name_img = "training0003.png"

list_CNN_num_class = [6, 5, 1]

result_CNN_dir = ["data/result/CNN_6_class",
				  "data/result/CNN_5_class",
				  "data/result/CNN_1_class"]

result_CNN_json_name = ["CNN_6_class",
				 		"CNN_5_class",
						"CNN_1_class"]

for i in range(len(list_CNN_num_class)):
	num_class = list_CNN_num_class[i]
	print(result_CNN_json_name[i])

	print("class\metrics", "jaccard", "dice", "RI", "Accuracy", "AdaptedRandError", "Fscore")
	json_list = [["class\metrics", "jaccard", "dice", "RI", "Accuracy", "AdaptedRandError", "Fscore"]]
	for index_label_name in range(num_class):
		original_name = os.path.join("data/original data/", mask_name_label_list[index_label_name], name_img)
		etal = io.imread(original_name, as_gray=True)
		etal = to_0_255_format_img(etal)
		if (etal.size == 0):
			print("error etal")

		test_img_name = "predict_"+name_img

		test_img_dir = os.path.join(result_CNN_dir[i], mask_name_label_list[index_label_name], test_img_name)
		img = io.imread(test_img_dir, as_gray=True)

		img = to_0_255_format_img(img)

		if (img.size ==0):
			print("error img")

		ret,bin_true = cv2.threshold(etal, 128, 255, 0)
		ret,bin_img_true = cv2.threshold(img, 128, 255, 0)


		#print(img)
		#print(etal)
		#viewImage(bin_true,"etal")
		#viewImage(bin_img_true,"img")

		y_true = bin_true.ravel()
		y_pred = bin_img_true.ravel()


		#blac
		ret,bin_pred1 = cv2.threshold(etal, 0, 0, 0)
		y_pred1 = bin_pred1.ravel()
		#Brez = jaccard_similarity_score(y_true, y_pred1)


		#white
		ret,bin_pred2 = cv2.threshold(etal, 255, 255, 1)
		y_pred2 = bin_pred2.ravel()
		#Wrez = jaccard_similarity_score(y_true, y_pred2)

		test =  jaccard(y_true, y_true)
		Brez2 = jaccard(y_true, y_pred1)
		Wrez2 = jaccard(y_true, y_pred2)


		#viewImage(y_pred1,"bitB")
		#viewImage(y_pred2,"bitW")

		#
		#print(Brez,Wrez)
		#print(Brez2,Wrez2, test)
		#cv2.waitKey(0)

		rez = jaccard(y_true, y_pred)
		rez2 = dice(y_true, y_pred)
		res3 = RI(y_true, y_pred)
		res4 = Accuracy(y_true, y_pred)
		res5 = Fscore(y_true, y_pred) #Adapted Rand Error

		print(mask_name_label_list[index_label_name], rez, rez2, res3, res4, 1-res5, res5)
		json_list.append([mask_name_label_list[index_label_name], rez, rez2, res3, res4, 1-res5, res5])

		cv2.waitKey(0)
		cv2.destroyAllWindows()

	with open(result_CNN_dir[i] + "/result_"+result_CNN_json_name[i]+ ".json", 'w') as file:
		json.dump(json_list, file)