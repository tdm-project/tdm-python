
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

const tiff_layer_name='Total Prec';
const tiff_layer_zindex=450;

const layer_order=[base_satellite_name,
		   tiff_layer_name];

function compare_layers(A,B,nameA,nameB) {
    let indexA=layer_order.indexOf(nameA);
    let indexB=layer_order.indexOf(nameB);
    if (indexA < indexB) return -1;
    if (indexA > indexB) return 1;
    return 0;
}

const tiff_min = 0;
const tiff_max = 6.4;
const tiff_domain = [0, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4];
const tiff_scale = chroma.scale(['rgba(30,60,255,0.0)',
				  'rgba(160,255,255,1.0)',
				  'rgba(160,255,255,1.0)',
				  'rgba(0,210,140,1.0)',
				  'rgba(0,220,0,1.0)',
				  'rgba(160,230,50,1.0)',
				  'rgba(230,175,45,1.0)',
				  'rgba(240,130,40,1.0)']).domain(tiff_domain);
const tiff_opacity=0.6;


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


async function setupTiffLayer(tiff_url) {
    let map = mapStuff.map;
    let layerControl = mapStuff.layerControl;

    return new Promise(async function(resolve, reject) {
	if(tiff_url) {
  	    const tiff_info= await getGeoTiff(tiff_url);
	    if(tiff_info) {
		tiffLayer= new TDMBasicGeotiffLayer("TDM_TIFF", {
		    width: tiff_info.width,
		    height: tiff_info.height,
		    geobounds: tiff_info.bounds,
		    channels: tiff_info.data,
    	            colorscale: tiff_scale,
		    opacity: tiff_opacity,
		    min_value: tiff_min,
		    max_value: tiff_max
		});
		layerControl.addOverlay(tiffLayer, tiff_layer_name);
    		tiffLayer.addTo(map);
		tiffLayer._canvas.style.zIndex = tiff_layer_zindex;
		resolve("OK");
	    } else {
		reject(Error("CANNOT LOAD "+tiff_url));
	    }
	} else {
	    resolve("OK");
	}
    });
}


// Main
async function main(geotiff_url) {
    mapStuff=initBaseMap();
    await setupTiffLayer(geotiff_url);
}

// TPREC
window.onload = function() {
    main("https://rest.tdm-project.it/tdm/odata/product/meteosim/moloch/AAABBBBCCC3090/2018-11-03_06:00:00/4.5:512:0.0226_36.0:512:0.0226/tprec.tif");
};

// RADAR
//window.onload = function() {
//    main("https://rest.tdm-project.it/tdm/odata/product/radar/cag01est2400/2018-08-07/low_res/2018-08-07_14:00:00/lon:8.751948:9.466604_lat:38.951127:39.505794/rainfall_rate/2018-08-07_14:00:00.tif");
//};

