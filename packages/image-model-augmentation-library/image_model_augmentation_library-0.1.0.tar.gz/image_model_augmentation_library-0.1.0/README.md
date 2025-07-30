# Image Augmentation Library #
Created by Dylan Tran


This library is intended to augment image datasets for model training purposes.

Example usage:
```
imageArr = readImageDirIntoArr(r"C:\Augmentation\test_images\msk_3_7")
startIdx = 0
for augArr in rectangleCrop(imageArr, 5):
    saveOutputs(r"C:\Augmentation\sample_output", augArr, startIdx)
    startIdx += len(augArr)

```