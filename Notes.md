*Context*
- Deforestation
	- Forest loss contributes nearly 5 billion tons of carbon dioxide into the atmosphere every year, which is equivalent to nearly 10% of annual human emissions
	- EU consumption of goods products on deforested land accounts for about 10% of global deforestation, mostly palm oil and soya, which account for more than two thirds
- New regulation
	- Therefore, new regulation on deforestation in EU - **EU Deforestation Regulation 2023/111** mandates companies importing certain commodities into the EU to provide evidence that they are free of deforestation - going into effect in December 2024
	- Companies ne, ed to trace their imported products back to the plot of land where they were sourced and collect the geographic coordinates of the plots where it can be proven that no deforestation has occured
	- Penalties for non-compliance may include *fines over 4% of turnover* within the EU + *exclusion to public funding* and *confiscation of goods*
	- Thus, businesses need robust and efficient systems capable of accurately *identifying and tracing the origins of their products* to ensure they meet the EU’s stringent deforestation-free standards
---
*Problem*
Ensuring products sourced from farms (soy from Brazil, palm oil from Malaysia & Indonesia) are deforestation free is difficult and unreliable with current traceability processes and thus can result in supporting illegal deforestation as well as huge fines for businesses.
---
*Solution*
- Web tool that allows companies to view their related sources for crops and see if/how much deforestation has occured within a certain timeframe
	- Scrolling through time
	- Segmentation and total amount of land lost
	- What this relates to in carbon losses
	- Classificiation of area whether or not it is legal (if amount lost over x timeframe is below or above EU threshold)
- This can then be used by companies to track their supply chains, as well as governmental bodies to ensure that companies are compliying with regulation
___
*Execution*
Segmentation and change detection of time series satellite images to classify which areas have been deforested
1. Collect satellite data (many free sources for raw images) or already processed satellite images (not recent however)
2. Create time series of said data over certain areas (need to limit this)
3. CNNs to classify which areas are forest
4. Change detection to classify which areas have become non-forest
5. Calculate and present metrics based on area of deforestation
---
*Similar projects*
- **ForestNet deforestation driver** (Jeremy Irvin, Hao Sheng et al., 2020) A dataset that consists of 2,756 LANDSAT-8 satellite images of forest loss events with deforestation driver annotations. The driver annotations were grouped into Plantation, Smallholder Agriculture, Grassland/shrubland, and Other.
	- ForestNet: Classifying Drivers of Deforestation in Indonesia using Deep Learning on Satellite Imagery
- **Global Forest Change** (University of Maryland, 2013) Different layers of global forest loss, extracted from Landsat satellite imagery
- **Awesome Remote Sensing Change Detection** - Github list of datasets, codes, and contests related to remote sensing change detection.
- **BigEarthNet: large-scale Sentinel-2 benchmark** (TU Berlin, 2019) A landcover multi-classification dataset from 10 European countries with ≈600k labeled images with CORINE land cover labels with Sentinel-2 L2A (10m res.) satellite imagery.
- **Kaggle Planet: Understanding the Amazon from Space** A land cover classification dataset from the Amazon with deforestation, mining, cloud labels with RGB-NIR (5m res.) satellite imagery.
- **Dynamic EarthNet challenge** A time-series prediction and multi-class change detection dataset of Europe over 2-years with 75 image time-series with 7 land-cover labels and weekly Planet RGB (3m res.) imagery.
- An attention-based U-Net for detecting deforestation within satellite sensor imagery
- Amazon forest cover change mapping based on semantic segmentation by U-Nets
- ResUNet-a: A deep learning framework for semantic segmentation of remotely sensed data
- Deforestation detection using deep learning-based semantic segmentation techniques: a systematic review
- USING TIME SERIES IMAGE DATA TO IMPROVE THE GENERALIZATION CAPABILITIES OF A CNN - THE EXAMPLE OF DEFORESTATION DETECTION WITH SENTINEL-2
- ![[Pasted image 20240516115746.png|225]] ![[Pasted image 20240516115809.png|325]]
- ==Amazon forest cover change mapping based on semantic segmentation by U-Nets https://sci-hub.yncjkj.com/10.1016/j.ecoinf.2021.101279 ![[Pasted image 20240516172744.png]]
- Image augmentation?
- Meta Segment Anything Model?
- ==Review on image segmentation papers - https://www.frontiersin.org/files/Articles/1300060/ffgc-07-1300060-HTML/image_m/ffgc-07-1300060-t003.jpg
---
*Data Sources*
- https://github.com/BioWar/Satellite-Image-Segmentation-using-Deep-Learning-for-Deforestation-Detection - 322 images and corresponding masks of forests and deforestation areas
-  https://zenodo.org/records/4498086 - # Amazon and Atlantic Forest image datasets for semantic segmentation
	- This database contains images from *Amazon* and *Atlantic Forest* brazilian biomes used for training a fully convolutional neural network for the semantic segmentation of forested areas in images from the Sentinel-2 Level 2A Satellite.
	- *Training dataset:* it contains 499 and 485 GeoTIFF images (Amazon and Atlantic Forest, respectively) with 512x512 pixels and associated PNG masks (forest indicated in white and background in black color).
	- *Validation dataset*: it contains 100 GeoTIFF images for each biome with 512x512 pixels and associated PNG masks used for validation step.
	- *Test dataset:* it contains 20 GeoTIFF images for each biome with 512x512 pixels for testing.
- https://zenodo.org/records/3233081 - Amazon Rainforest dataset for semantic segmentation - collection of RGB-converted images and deforestation masks, where 0s and 1s represent non-forest and forest areas respectively, of the Amazon Rainforest (Bragagnolo et al., 2019)
	- *Training dataset:* it contains 30 GeoTIFF images with 512x512 pixels and associated PNG masks (forest indicated in white and non-forest in black color)
	- *Validation dataset*: it contains 15 GeoTIFF images with 512x512 pixels and associated PNG masks used for U-Net validation step.
	- *Test dataset:* it contains 15 GeoTIFF images 512x512 pixels for testing.
- https://www.kaggle.com/c/planet-understanding-the-amazon-from-space - rainforest imgs with classifications (tree, tree with road, plantation, cloud)
---
*Training data*
- https://zenodo.org/records/4498086 - # Amazon and Atlantic Forest image datasets for semantic segmentation
	- This database contains images from *Amazon* and *Atlantic Forest* brazilian biomes used for training a fully convolutional neural network for the semantic segmentation of forested areas in images from the Sentinel-2 Level 2A Satellite.
	- *Training dataset:* it contains 499 and 485 GeoTIFF images (Amazon and Atlantic Forest, respectively) with 512x512 pixels and associated PNG masks (forest indicated in white and background in black color).
	- *Validation dataset*: it contains 100 GeoTIFF images for each biome with 512x512 pixels and associated PNG masks used for validation step.
	- *Test dataset:* it contains 20 GeoTIFF images for each biome with 512x512 pixels for testing.
- TIFF files are much more data-rich than JPG
-  GeoTIFF - *a public domain metadata standard that enables georeferencing information to be embedded within an image file*. The GeoTIFF format embeds geospatial metadata into image files such as aerial photography, satellite imagery, and digitized maps so that they can be used in GIS applications.
---
*Application data*
- Sentinel-2 L2A
- Every 5 days
- Cloud cover filter
- Up to 9m/px resolution
https://apps.sentinel-hub.com/eo-browser/?zoom=12&lat=-9.97798&lng=-55.10433&themeId=MONITORING&visualizationUrl=https%3A%2F%2Fservices.sentinel-hub.com%2Fogc%2Fwms%2F4e7f012a-5920-47bc-a0f1-7f075152f077&datasetId=S2L2A&fromTime=2024-05-15T00%3A00%3A00.000Z&toTime=2024-05-15T23%3A59%3A59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22#search
![[Pasted image 20240520100009.png]]
![[Pasted image 20240520100148.png]]
---
*Questions*
- Real-time access to sattelite data too costly cmoputationally - store images somewhere? How many? How big of an area to cover?
____
**Notes
- Cutoff date Dec 2020
	- https://www.nadar.earth/blog/why-gfw-is-not-suited-for-eudr-compliance
- How much is allowed? Below a certain threshhold?
- Slider to adjust model
- Classifier to determine whether an operation is under the threshold of what’s allowed
- ResNet model good
	- https://datagen.tech/guides/computer-vision/resnet-50/#
---
*Further development:*
-  https://www.nadar.earth/blog/why-gfw-is-not-suited-for-eudr-compliance
- Not possible to understand the true cause of forest loss
	- Legal expansion (edited) 
