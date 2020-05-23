from flask import escape
from flask import Flask
import logging
import json
import colorsys as csys
import matplotlib as mp
import seaborn as sns
import pandas as pd
from flask import Response
from flask import jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


def lighter(color, ratio):
    c = csys.rgb_to_hls(*mp.colors.to_rgb(color))
    rgb = csys.hls_to_rgb(c[0], c[1] + (1 - c[1]) * ratio, c[2])
    return mp.colors.to_hex(rgb)


def darker(color, ratio):
    c = csys.rgb_to_hls(*mp.colors.to_rgb(color))
    rgb = csys.hls_to_rgb(c[0], c[1] - c[1] * ratio, c[2])
    return mp.colors.to_hex(rgb)


def lighterAndDarkerList(color, ratios):
    return list(map(lambda ratio: lighter(color, ratio), ratios)) + list(map(lambda ratio: darker(color, ratio), ratios))


def fullSpectrumRow(args, ratios):
    name, color = args
    print("mainFunc -> ", [name, color] + lighterAndDarkerList(color, ratios))
    return [name, color] + lighterAndDarkerList(color, ratios)


def fullSpectrumForPrimaryColorsTable(dataset):
    colors = list(
        map(lambda tuple: [tuple.ColorID, tuple.ColorHex], dataset.itertuples()))

    ratios = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]

    allData = list(map(lambda args: fullSpectrumRow(args, ratios), colors))

    return pd.DataFrame(
        allData,
        columns=['ColorID', 'ColorHex'] + list(map(lambda ratio: "Lighten_" + str(ratio), ratios)) + list(map(lambda ratio: "Darken_" + str(ratio), ratios)))


def get_theme_spectrum_for_colors(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        A csv with a full spectrum of the primary colors received. Call without body to see an example
        of response.
    """
    request_json = None
    try:
        request_json = request.get_json()
    except:
        app.logger.info('No Json...')

    if request_json:
        app.logger.info('Processing json colors in...')
        app.logger.info(json.dumps(request_json, indent=4))
        app.logger.info(type(request_json))

        dataset = pd.DataFrame(request_json)

        df = fullSpectrumForPrimaryColorsTable(dataset)

        return Response(
            df.to_csv(index=False),
            mimetype="text/csv")

    else:
        app.logger.info(
            'No json Detected. Please send a table of primary colors as shown below:')
        colorsData = [
            ['Primary_1', "#118DFF"],
            ['Primary_2', "#750985"],
            ['Primary_3', "#C83D95"],
        ]

        df = pd.DataFrame(colorsData, columns=['ColorID', 'ColorHex'])
    
        jsonData = df.to_json(orient='records')

        return """
            No json Detected. Please send as input a json table of primary colors as shown below:
    
            {jsonTable}
            """.format(jsonTable=jsonData)
