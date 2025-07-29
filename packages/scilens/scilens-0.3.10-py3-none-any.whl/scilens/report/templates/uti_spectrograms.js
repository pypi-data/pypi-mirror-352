((w_1, undef) => {
//
// tmp
//
function resize22(obj, parent, dir) { // ASSUMPTIONS : obj.size int, "js-plotly-plot"
  // size
  const w = obj.size[0] + (dir * obj.size[0] * 0.1);
  const h = obj.size[0] + (dir * obj.size[0] * 0.1);
  obj.size = [w, h];
  // update widgets
  const update = { width: w, height: h };
  const nodes = dom.q(parent, ".js-plotly-plot");
  nodes.forEach((node) => {
    node.style.width  = w + "px";
    node.style.height = h + "px";
    Plotly.relayout(node, update); // update plotly
  });
}
//
//
//
const PREFIX = "spectrograms_"; // section prefix
const COLORSCALE = "Viridis"; // plotly
const COLORSCALE_DIFF = "RdBu"; // plotly
const CFG = {
  "DISPLAY_TESTREF": true, // display test reference
  "DISPLAY_DIFF": true, // display diff
  "WIDTH": 300, // default width
  "HEIGHT": 300, // default height
}

//
class Spectrograms {
  constructor(index, arr_mat) {
    //console.log("index data", index);
    // data
    this.size = [CFG.WIDTH, CFG.HEIGHT]; // default size
    this.arr_mat = arr_mat;
    this.elt = dom.get(PREFIX+(1+index));
    // init
    this.init();
  }
  init() {
    // resize
    const that = this;
    //
    const tmpls = []
    this.arr_mat.forEach((mat, i) => { tmpls.push({tag:"button", html: mat.name, click: function() { that.var_toogle(i); } }) });
    //
    dom.tree(
      this.elt,
      {tag:"div", children: [
        {tag:"div", attrs:{class:"py-2"}, children: [
          {tag:"button", html: '+ Increase', click: function() { resize22(that, that.elt, 1); }},
          {tag:"button", html: '- Decrease', click: function() { resize22(that, that.elt, -1); }},
        ]},
        {tag:"div", attrs:{class:"py-2"}, children: tmpls},  
      ]},
    );
    // toogle
    // Show all
    this.arr_mat.forEach((mat, i) => { this.var_add(i); });
  }
  var_get_id(idx) {
    return PREFIX+"block_"+idx;
  }
  var_toogle(idx) {
    if (dom.get(this.var_get_id(idx))) { this.var_rmv(idx); }
    else { this.var_add(idx); }
  }
  var_add(idx) {
    const mat = this.arr_mat[idx];
    //
    const style = "width:"+this.size[0]+"px;height:"+this.size[1]+"px;";
    const attrs = { class: "m-1 shadow-lg" };
    //
    const templs = [];
    if (CFG.DISPLAY_TESTREF) templs.push({out:"var", tag:"div", attrs: attrs, style:style});
    if (mat.ref) {
      if (CFG.DISPLAY_TESTREF) templs.push({out:"ref", tag:"div", attrs: attrs, style:style});
      if (CFG.DISPLAY_DIFF) templs.push({out:"dif", tag:"div", attrs: attrs, style:style});
    }
    const e = {};
    dom.tree(
      this.elt,
      {tag:"div", attrs: {id: this.var_get_id(idx)}, children: [
          {tag:"div", style:"display: flex; flex-wrap: wrap;", children: templs},
      ]},
      e
    );

    if (CFG.DISPLAY_TESTREF) this.add_widget(e["var"], mat, mat.data);
    if (mat.ref) {
      if (CFG.DISPLAY_TESTREF) this.add_widget(e["ref"], mat, mat.ref, " - Ref.");
      if (CFG.DISPLAY_DIFF) this.add_widget(e["dif"], mat, mat.ref_diff_abs_data(), " - Diff.", COLORSCALE_DIFF);
    }
  }
  var_rmv(idx) {
    dom.get(this.var_get_id(idx)).remove();
  }
  add_widget(elt, mat, matdata, suffix="", colorscale=COLORSCALE) {
    const data = [{
        z: matdata,
        type: 'heatmap',
        colorscale: colorscale,
    }];

    const layout = {
        title: mat.name + suffix,
        xaxis: { title: mat.x_name || 'X' },
        yaxis: { title: mat.y_name || 'Y' },
    };

    Plotly.newPlot(elt, data, layout);        
  }
}
Spectrograms.config = function(cfg) {for (k in cfg) {CFG[k] = cfg[k];}};
w_1.Spectrograms = Spectrograms;
})(window);