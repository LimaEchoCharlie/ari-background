#!/usr/bin/env python3

from os import getenv, path, getcwd
from subprocess import run, DEVNULL
from requests import get
from platform import system
from PIL import Image
from io import BytesIO

PROCESS_TIMEOUT = 10
REQUEST_TIMEOUT = 20

def getPic(date = None):
    """ Get picture and save it to a local subfolder called pictures 
    :param date: Date in format %Y-%m-%d (eg 2017-02-18) of the Astronomy Picture of the Day. Default is today.
    """

    # get api key - default to NASA demo key
    apiKeyVal = getenv( 'NASA_API_KEY', default='DEMO_KEY')

    try:
        # get meta data from NASA API
        metaResponse = get( 'https://api.nasa.gov/planetary/apod', 
                            params={'date':date, 'api_key' : apiKeyVal}, 
                            timeout=REQUEST_TIMEOUT)

        metaData = metaResponse.json()

        # only get images
        if metaData['media_type'] != 'image':
            print('Not an image')
            print( metaData )
            return None

        # get image
        picResponse = get( metaData['hdurl'], timeout=REQUEST_TIMEOUT )
        picture = Image.open(BytesIO(picResponse.content))

        # print explanation
        print( metaData['explanation'])

        # save image to pictures subdirectory
        picPath = path.join( getcwd(), 'pictures', metaData['hdurl'].split('/')[-1] )
        picture.save( picPath )

        return {'path':picPath, 'landscape': picture.width > picture.height}


    except Exception as err:
        print( "GET failed" )
        print( err )
        return None

if __name__ == '__main__':
    if system() != 'Darwin':
        exit(1)
        
    pic = getPic()

    if pic is not None and pic['landscape']:
        osaSetPicCmd = 'tell application "Finder" to set desktop picture to "%s" as POSIX file'% pic['path']
        progRet = run( ['osascript',"-e", osaSetPicCmd], stderr=DEVNULL, timeout=PROCESS_TIMEOUT )
