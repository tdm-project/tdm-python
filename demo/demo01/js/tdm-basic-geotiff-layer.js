// WEBGL DEBUG UTILITY
function logGLCall(functionName, args) {   
   console.log("gl." + functionName + "(" + 
      WebGLDebugUtils.glFunctionArgsToString(functionName, args) + ")");   
}

// UTILITY 
function clamp(v, min, max) {
  return Math.min(Math.max(v, min), max);
};

//////////////////////////////////////////////////////////////////////////

var TDMBasicGeotiffLayer = L.TDMCanvasLayer.extend({

    options: {
        width: 0,
	height: 0,
	geobounds: null,
	channels: null,
	colorscale: chroma.scale(['rgba(0,0,0,0.0)', 'rgba(255,255,255,1.0)']),
	min_value: 0.0,
	max_value: 1.0,
	opacity: 1.0,
	webgl_debug: false
    },

    _gl: null,
    _buffer_info: null,
    _texture: null,
    _texture_palette: null,
    _uniforms: {
	u_matrix: null,
	u_rgba: null,
	u_palette: null
    },
    _shaders_prg: null,
    _vs: `
          uniform mat4 u_matrix;

          attribute vec3 a_position;
          attribute vec2 a_texcoord;

          varying vec2 v_texCoord;
	 
          void main() {
	     //gl_Position = vec4(a_position, 1.0);
	     gl_Position = u_matrix * vec4(a_position, 1.0);
	     v_texCoord = a_texcoord;
	  }`,
    _fs: `
	 precision mediump float;
	 
	 varying vec2 v_texCoord;
	 
	 uniform sampler2D u_rgba;
	 uniform sampler2D u_palette;

	 void main(void) {
             float v = texture2D(u_rgba, v_texCoord).a;
             gl_FragColor = texture2D(u_palette, vec2(v, 0.5));
  	 }`,
    _LatLongToPixelXY: function (latitude, longitude) {
	var pi_180 = Math.PI / 180.0;
	var pi_4 = Math.PI * 4;
	var sinLatitude = Math.sin(latitude * pi_180);
	var pixelY = (0.5 - Math.log((1 + sinLatitude) / (1 - sinLatitude)) / (pi_4)) * 256;
	var pixelX = ((longitude + 180) / 360) * 256;
	var pixel = { x: pixelX, y: pixelY };
	return pixel;
    },
    _gl_init: function() {
	if (!this._gl) {
	    this._canvas.width = this._canvas.clientWidth;
	    this._canvas.height = this._canvas.clientHeight;
	    var names = [ "webgl", "experimental-webgl", "moz-webgl", "webkit-3d" ];
	    for (var i=0; names.length>i; i++) {
		try { 
		    this._gl = this._canvas.getContext(names[i], {premultipliedAlpha: false});
		    if (this._gl) {
			if (this.options.webgl_debug) {
			    this._gl = WebGLDebugUtils.makeDebugContext(this._gl, undefined, logGLCall);
			}
			break;
		    }
		} catch (e) {
		    alert("ERROR: OpenGL context not detected!");
		}
	    }
	}
	twgl.setDefaults({attribPrefix: "a_"});
    },
    _gl_create_rendering_objects: function() {
	this._shaders_prg = twgl.createProgramInfo(this._gl, [this._vs, this._fs]);

	let verts = [];
	pixel00 = this._LatLongToPixelXY(this.options.geobounds[0][0], this.options.geobounds[0][1]);
	pixel11 = this._LatLongToPixelXY(this.options.geobounds[1][0], this.options.geobounds[1][1]);
	verts.push(pixel00.x, pixel00.y, 0.0);
	verts.push(pixel11.x, pixel00.y, 0.0);
	verts.push(pixel11.x, pixel11.y, 0.0);
	verts.push(pixel00.x, pixel11.y, 0.0);

	let quad_arrays = {
	    position: { numComponents: 3, data: verts },
	    texcoord: { numComponents: 2, data: [0, 0, 1, 0, 1, 1, 0, 1] },
	    indices: [0,2,3,0,1,2]
	};

	this._buffer_info = twgl.createBufferInfoFromArrays(this._gl, quad_arrays);

	// Palette
	let palette = new Uint8Array(256 * 4);
	let vmin=this.options.min_value;
	let vmax=this.options.max_value;
	let cscale = this.options.colorscale;
	for (let i=0; i<256; i++) {
	    let v = vmin+i/255*(vmax-vmin);
	    let c = cscale(v).rgba();
	    let r = c[0];
	    let g = c[1];
	    let b = c[2];
	    let a = c[3]*this.options.opacity*255;
	    palette[i*4+0]=r;
	    palette[i*4+1]=g;
	    palette[i*4+2]=b;
	    palette[i*4+3]=a;
	}

	this._texture_palette = twgl.createTexture(this._gl, {
	    src: palette,
	    width: 256,
	    height: 1,
	    type: this._gl.UNSIGNED_BYTE,
	    format: this._gl.RGBA,
	    internalFormat: this._gl.RGBA,
	    wrapS: this._gl.CLAMP_TO_EDGE,
	    wrapT: this._gl.CLAMP_TO_EDGE
	}, function() {
	    this._uniforms.u_palette = this._texture_palette;
	});

	// Data
	let w=this.options.width;
	let h=this.options.height;
	let delta=vmax-vmin;
	if (vmax === vmin) console.log("ERROR: max_value is equal to min_value"); 
	let tmp_texture_a = new Uint8Array(w*h*1);
	let idx=0;
	for (let j = 0; j<h; j++) {
	    for (let i = 0; i<w; i++) {
		let original_value=this.options.channels[0][i + j*w];
		let v = 0;
		if (original_value != -1) {
		    v = clamp(Math.round((original_value-vmin)/delta*255), 0.0, 255.0);
		}
		tmp_texture_a[idx+0] = v;
		//if(i<10 && j<10) console.log(i+ " "+j+ " ["+idx+ "] -> "+v);
		idx=idx+1;
	    }
	}
	this._texture = twgl.createTexture(this._gl, {
	    src: tmp_texture_a,
	    width: w,
	    height: h,
	    type: this._gl.UNSIGNED_BYTE,
	    format: this._gl.ALPHA,
	    internalFormat: this._gl.ALPHA,
	    wrapS: this._gl.CLAMP_TO_EDGE,
	    wrapT: this._gl.CLAMP_TO_EDGE
	}, function() {
	    this._uniforms.u_rgba = this._texture;
	});
	
    },
    _gl_destroy_rendering_objects: function() {
	// delete shaders
	this._shaders_prg = null;
	//delete vertex buffer
	this._buffer_info = null;
	// delete texture
	this._texture = null;
	this._texture_palette = null;	
	this._uniforms.u_rgba = null;
    },
    _gl_render: function() {
	if (!this._gl) return;
	if (!this._buffer_info) return;
	
	twgl.resizeCanvasToDisplaySize(this._gl.canvas);

	this._gl.viewport(0, 0, this._gl.canvas.width, this._gl.canvas.height);
	this._gl.clearColor(0.0, 0.0, 0.0, 0.0);
	this._gl.clear(this._gl.COLOR_BUFFER_BIT | this._gl.DEPTH_BUFFER_BIT);
	
	const mapMatrix = [2 / this._gl.canvas.width, 0, 0, 0,
			   0, -2 / this._gl.canvas.height, 0, 0,
			   0, 0, 0, 0,
			   -1, 1, 0, 1]; 
	let bounds = this._map.getBounds();
	let topLeft = new L.LatLng(bounds.getNorth(), bounds.getWest());
	let offset = this._LatLongToPixelXY(topLeft.lat, topLeft.lng);    
	let scale = Math.pow(2, this._map.getZoom());

	twgl.m4.scale(mapMatrix, [scale,scale,1.0], mapMatrix);
	twgl.m4.translate(mapMatrix, [-offset.x,-offset.y,0.0], mapMatrix);
	this._uniforms.u_matrix=mapMatrix;
	this._uniforms.u_rgba = this._texture;
	this._uniforms.u_palette = this._texture_palette;
	
	this._gl.useProgram(this._shaders_prg.program);

	twgl.setBuffersAndAttributes(this._gl, this._shaders_prg, this._buffer_info);
	twgl.setUniforms(this._shaders_prg, this._uniforms);
	
	twgl.drawBufferInfo(this._gl, this._gl.TRIANGLES, this._buffer_info);
    },
    initialize: function(name, options) {
        this.name = name;
        L.setOptions(this, options);
    },
    onLayerDidMount: function () {
        var topLeft = this._map.containerPointToLayerPoint([0, 0]);
	L.DomUtil.setPosition(this._canvas, topLeft);
	if (!this._gl) this._gl_init();
	this._gl_create_rendering_objects();
    },
    onLayerWillUnmount: function() {
	this._gl_destroy_rendering_objects();
	this._gl.getExtension('WEBGL_lose_context').loseContext(); // Force immediate release of context...
	this._gl=null;
    },
    onDrawLayer: function(info) {
	this._gl_render();
    }
    
});

