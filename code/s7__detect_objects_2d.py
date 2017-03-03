"""
Reads:
 - Clipped images
    - location: see output from previous step
    - format: see output from previous step
    - read with: opencv imread
 - Classifier definition (.xml)
    - location: defined by user in settings file
    - format: XML
    - read with: opencv CascadeClassifier
Writes:
 - For each image, a collection of 2D prediction points
    - format: GeoJSON
    - location: [project home directory]/4_detect_objects_2d/
Tasks:
 - Read detection scale range from settings (at what pixel scale should objects be detected?)
 - For each image
   - [optional] determine optimal detection scale from image height
   - Run classifier
   - Convert prediction rectangles into points
   - transform points back into 3D space
   - Save prediction points for that image
Tools:
 - OpenCV CascadeClassifier.exe
 - Parallel? This processing step is arguably the most lengthy and the one that will be repeated many times.
"""

import cv2
import os
import numpy as np
from helpers import readGeoTiff
import default_settings as settings


def detect_objects_2d(config, debug):
    # clipped images from preparations task are stored here
    image_folder = os.path.join(settings.general['working_directory'],
                                settings.general['preparations_subdir'],
                                settings.general['preparations_structure'][2])

    # detected locations should be stored here
    output_folder = os.path.join(config['iteration_directory'],
                                 settings.general['iterations_structure'][2])

    # classifier data found here
    classifier_xml = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][1],
                                            'cascade.xml')


    # loop through each image
    for image_file in os.listdir(image_folder):
        image_name = os.path.splitext(image_file)[0]
        cascade_detect(
            image_name,
            os.path.join(image_folder, image_file),
            output_folder,
            classifier_xml)

    return 0


# Function for detecting objects
def cascade_detect(image_name, image_file, output_folder, classifier_xml):
    # Load classifier from data
    object_detector = cv2.CascadeClassifier(classifier_xml)
    # Check that it was successful
    if object_detector.empty():
        print 'classifier not loaded - stopping script'
        quit()

    # read image
    image, origin, cell_size, dimensions = readGeoTiff(image_file)

    # detect objects
    detection_results = object_detector.detectMultiScale3(
        image,
        scaleFactor=1000000,
        minNeighbors=1,
        outputRejectLevels=True
    )
    rects = detection_results[0]
    neighbors = detection_results[1]
    score = detection_results[2]
    print len(rects), ' object(s)'

    # save under this filename
    output_file = os.path.join(output_folder, image_name + '.csv')
    # save to csv
    write_data2csv(rects, score, origin, cell_size, output_file)


def write_data2csv(rects, score, origin, cell_size, output_file):
    '''Writes CSV from a list of rectangle objects.'''

    points = np.empty([len(rects), 4])  # 4 columns: x and y, score, and id

    for i in range(len(rects)):
        (x, y, w, h) = rects[i]
        # Calculate centroid location in image coordinates
        x2d = (x + w / 2) * cell_size[0] + origin[0]
        y2d = (y + h / 2) * cell_size[1] + origin[1]

        # Write to array, with
        points[i] = [x2d, y2d, score[i], i]

        # write to CSV
        np.savetxt(output_file, points, header="x;y;n;id", delimiter=";", comments='')

    print 'objects written to ', output_file
