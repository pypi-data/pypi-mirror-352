((w_1, undef) => {

//
//
//
const PREFIX = "frameseries_"; // section prefix
const CFG = {
  "WIDTH": 300, // default width
  "HEIGHT": 300, // default height
}

//
class Frameseries {
  constructor(index, arr_mat, frames_vector) {
    // DEBUG
    // console.log("index", index);
    // console.log("arr_mat", arr_mat);
    // console.log("frames_vector", frames_vector);
    // data
    this.size = [CFG.WIDTH, CFG.HEIGHT]; // default size
    this.arr_mat = arr_mat;
    this.elt = dom.get(PREFIX+(1+index));
    // frames
    if (frames_vector) {
      this.frame_len = frames_vector.length;
      this.frame_min = frames_vector[0];
      this.frame_max = frames_vector[this.frame_len-1];
    } else {
      this.frame_len = arr_mat[0].data.length;
      this.frame_min = 0;
      this.frame_max = this.frame_len-1;
    }
    // init
    this.init();
  }
  init() {
    // resize
    const that = this;
    //
    // const tmpls = []
    // this.arr_mat.forEach((mat, i) => { tmpls.push({tag:"button", html: mat.name, click: function() { that.var_toogle(i); } }) });
    const tmpls = data.arr_mat.map((x,i) => { return {out:"variable_"+i, tag:"div", style:"width:"+this.size+"px;height:"+this.size+"px;"} ; } );


  }
  var_get_id(idx) {
    return PREFIX+"block_"+idx;
  }
  var_toogle(idx) {
    if (dom.get(this.var_get_id(idx))) { this.var_rmv(idx); }
    else { this.var_add(idx); }
  }
  var_add(idx) {
  }
  var_rmv(idx) {
    dom.get(this.var_get_id(idx)).remove();
  }
}
Frameseries.config = function(cfg) {for (k in cfg) {CFG[k] = cfg[k];}};
w_1.Frameseries = Frameseries;
})(window);