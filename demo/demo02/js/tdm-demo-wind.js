
async function getGeoTiff(url) {
    let tiffInfo=null;
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const tiff = await GeoTIFF.fromArrayBuffer(arrayBuffer);

    let image = await tiff.getImage();
    let rasters = await image.readRasters();

    let tiffWidth = image.getWidth();
    let tiffHeight = image.getHeight();
    let tiepoint = image.getTiePoints()[0];


    let pixelScale = image.getFileDirectory().ModelPixelScale;
    let geoTransform = [tiepoint.x, pixelScale[0], 0, tiepoint.y, 0, -1*pixelScale[1]];
    let imageBounds = [[geoTransform[3], geoTransform[0]], [geoTransform[3] + tiffHeight*geoTransform[5], geoTransform[0] + tiffWidth*geoTransform[1]]];

    tiffInfo = {
	width: tiffWidth,
	height: tiffHeight,
	bounds: imageBounds,
	data: rasters
    }
    return tiffInfo;
}



////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////
//
// GLOBAL VARIABLES

let mapStuff = null;
const base_satellite_name='Satellite';

const wind_layer_name='10m Wind';
const wind_layer_zindex=450;

const layer_order=[base_satellite_name,
		   wind_layer_name];

function compare_layers(A,B,nameA,nameB) {
    let indexA=layer_order.indexOf(nameA);
    let indexB=layer_order.indexOf(nameB);
    if (indexA < indexB) return -1;
    if (indexA > indexB) return 1;
    return 0;
}

const wind_min_speed = 0;
const wind_max_speed = 20; // 30 m/s right value
const wind_scale = chroma.scale(['#3288bd',
				 '#66c2a5',
				 '#abdda4',
				 '#e6f598',
				 '#fee08b',
				 '#fdae61',
				 '#f46d43',
				 '#d53e4f']).domain([wind_min_speed, wind_max_speed]);    


////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////

function initBaseMap(){

    let Esri_WorldImagery = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles: ESRI &mdash; Data: NCEP NOAA, IISAC CNR Bologna, CRS4, UNICA'
    });

    let baseLayers = {
        'Satellite': Esri_WorldImagery,
    };

    let map = L.map('map', {
        layers: [ Esri_WorldImagery ],
	zoomControl: false
    });
    
    let layerControl = L.control.layers(
	baseLayers,          // base layers
	null,                // overlay layers
	{ 
	  autoZIndex: false,
	  sortLayers: true,
	  sortFunction: compare_layers,
	} // sort layers by name
    );
    layerControl.addTo(map);

    map.setView([39.195, 9], 10);
  
    return {
        map: map,
        layerControl: layerControl
    };
}

async function setupWindLayer(wind_url) {
    let map = mapStuff.map;
    let layerControl = mapStuff.layerControl;

    return new Promise(async function(resolve, reject) {
	if(wind_url) {
  	    const wind_info= await getGeoTiff(wind_url);
	    //await sleep(10000);
	    if(wind_info) {
		let cscale = [];
		for (let i = wind_min_speed; i <= wind_max_speed; i++) {
		    cscale.push(wind_scale(i).hex());
		}
	    
		let velocityLayer = L.velocityLayer({
		    displayValues: true,
		    displayOptions: {
			velocityType: '10m Wind',
			position: 'bottomleft',//REQUIRED !
			emptyString: 'No velocity data',//REQUIRED !
			angleConvention: 'bearingCW',//REQUIRED !
			displayPosition: 'bottomleft',
			displayEmptyString: 'No velocity data',
			speedUnit: 'm/s'
		    },
		    width: wind_info.width,
		    height: wind_info.height,
		    geobounds: wind_info.bounds,
		    data: wind_info.data,
		    minVelocity: wind_min_speed,          // used to align color scale
		    maxVelocity: wind_max_speed,          // used to align color scale
		    velocityScale: 0.005,        // modifier for particle animations, arbitrarily defaults to 0.005
		    colorScale: cscale,         // define your own function of hex/rgb colors
		    particleAge: 16,            // default 64
		    particleMultiplier: 1/200,  // default 1/300 (particles/pixels);
		    lineWidth: 2,                // default 1
		});
		layerControl.addOverlay(velocityLayer, wind_layer_name);
		velocityLayer.addTo(map);
		velocityLayer._canvasLayer._canvas.style.zIndex = wind_layer_zindex;		
		resolve("OK");
	    } else {
		reject(Error("CANNOT LOAD "+wind_url));
	    }
	} else {
	    resolve("OK");
	}
    });
}

// Main
async function main(geotiff_url) {
    mapStuff=initBaseMap();
    await setupWindLayer(geotiff_url);
}

// WIND
window.onload = function() {
    main("https://rest.tdm-project.it/tdm/odata/product/meteosim/moloch/AAABBBBCCC3090/2018-11-03_06:00:00/4.5:512:0.0226_36.0:512:0.0226/uv10.tif");
};

