/* cyder.models have been upgrade to use vue.js instead of viewlib.js (code in viewer.js)
However cyder.project still have some dependencies from the old viewer.js using viewlib.js
So we keep this legacy file until cyder.project is rewrite to use vue.js */

'use strict';
import { createAllModelsLayer, createModelLayer, createLoadHeatmapLayer } from './layers.js';
import { View, FOREACH, IF, ESCHTML } from '../viewlib.js';
import CyderAPI from '../api.js';

export class SelectModel extends View {
    constructor(el, allowEmpty = true) {
        super(el, 'span');
        this.allowEmpty = allowEmpty;
        let prom = CyderAPI.Model.getAll();
        if(prom instanceof Promise)
            this._ready = prom.then(() => { this.render() });
        else
            this._ready = Promise.resolve();
        this.render();
    }
    reloadModels() {
        return this._ready = CyderAPI.Model.getAll(true)
            .then(() => { this.render(); });
    }
    get ready() { return this._ready; }
    onchange(e) {}
    get _template() {
        let models = CyderAPI.Model.getAll();
        return `
        <select data-name="select" data-on="change:onchange" class="custom-select">
            ${ IF(this.allowEmpty, () => `<option value=""></option>` )}
            ${ IF(!(models instanceof Promise), () =>
                FOREACH(models.keys(), (modelName) =>
                    `<option value"${ESCHTML(modelName)}">${ESCHTML(modelName)}</option>`
                )
            )}
        </select>`;
    }
    get modelName() { return this._html.select.value }
    set modelName(val) { this.ready.then(() => this._html.select.value = val); }
}


import {Spinner} from './spin.js';
export class LeafletMap extends View {
    constructor(el) {
        super(el, 'div');
        this._layers = new Map();
        this._loadingLayers = 0;
        this._lastLayer = null;
        this._loadingSpinner = new Spinner();
        this.render();
    }
    _updateLoadingLayers(val) {
        this._loadingLayers += val;
        if(this._loadingLayers > 0)
            this._loadingSpinner.spin(this._html.el);
        else
            this._loadingSpinner.stop();
    }
    render() {
        super.render();
        this._map = L.map(this._html.el, {preferCanvas: true}).setView([37.8,-122.0], 9);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(this._map);
    }
    emplace(el) {
        super.emplace(el);
        this._map.invalidateSize();
    }
    get map() { return this._map; }
    addLayer(layer, name, keepOrder = false) {
        if(this._layers.has(name))
            throw new Error("A layer with this name already ");

        let isAddedProm = (async () => {
            this._updateLoadingLayers(+1);
            if(keepOrder && this._lastLayer !== null)
                await this._layers.get(this._lastLayer);
            layer = await layer;
            if(isAddedProm !== undefined && this._layers.get(name) !== isAddedProm)
                return false; // The layer have been removed while loading
            layer.addTo(this._map);
            this._layers.set(name, layer);
            this._updateLoadingLayers(-1);
            return true;
        })();
        this._lastLayer = name;
        if(this._layers.has(name))
            return true;
        this._layers.set(name, isAddedProm);
        return isAddedProm;
    }
    removeLayer(name) {
        let layer = this._layers.get(name);
        if(!layer)
            return false;
        this._layers.delete(name);
        if(this._lastLayer === name) {
            this._lastLayer = null;
            for(let name of this._layers.keys()) this._lastLayer = name;
        }
        if(layer instanceof Promise)
            this._updateLoadingLayers(-1);
        else
            layer.remove();
        return true;
    }
    removeLayers() {
        for(let layerName of this._layers.keys())
            this.removeLayer(layerName);
    }
    async fitBounds(name) {
        let layer = this._layers.get(name);
        if(layer instanceof Promise) {
            let isAddedProm = layer;
            if((await isAddedProm) === false)
                return false; // The layer have been removed while loading
            layer = this._layers.get(name);
        }
        this._map.fitBounds(layer.getBounds());
        return true;
    }
}

export class ModelViewer extends View {
    constructor(url, el) {
        super(el, 'div');
        this.url = url;
        this._childviews['select-model'] = new SelectModel();
        this.childview('select-model').onchange = (e) => {
            this.modelName = this.childview('select-model').modelName;
        };
        this._childviews['leaflet-map'] = new LeafletMap();
        this._childviews['model-info'] = new ModelInfo(this.childview('leaflet-map'));
    }
    get modelName() { return this._modelName; }
    set modelName(newModelName) {
        if(newModelName === this._modelName)
            return;
        if(this._modelName !== undefined && this._modelName === '')
            this.childview('leaflet-map').removeLayer('allModel');
        this._modelName = newModelName;
        if (this._modelName === '') {
            this.childview('model-info').model = null;
            this.childview('leaflet-map').addLayer(this._getAllModelsLayer(), 'allModel');
            this.childview('leaflet-map').fitBounds('allModel');
            history.replaceState(null, null, this.url);
        } else {
            Promise.resolve(CyderAPI.Model.getAll()).then((models) => {
                let model = models.get(this._modelName);
                if(model === undefined)
                    $.notify({title: `<strong>Not Found:</strong>`, message: "Not Found"},{type: 'danger'});
                else
                    this.childview('model-info').model = model;
            });
            history.replaceState(null, null, `${this.url}${this._modelName}/`);
        }
        this.childview('select-model').modelName = this._modelName;
    }
    _getAllModelsLayer() {
        if (this._allModelsLayerProm)
            return this._allModelsLayerProm;
        let addModelPopup = (feature, layer) => {
            let popup = new OpenModelPopup(feature.properties.modelname, this);
            layer.bindPopup(popup.el);
        };
        return this._allModelsLayerProm = createAllModelsLayer(addModelPopup);
    }
    get _template() {
        return `
        Select a model to display: <span data-childview="select-model"></span>
        <div data-childview="leaflet-map" style="height: 70vh; margin: 1rem 0 1rem 0;"></div>
        <div data-childview="model-info"></div>`;
    }
}

class OpenModelPopup extends View {
    constructor(modelName, modelViewer) {
        super(null, 'div');
        this.modelName = modelName;
        this.modelViewer = modelViewer;
        this.render();
    }
    onopen(e) {
        this.modelViewer.modelName = this.modelName;
    }
    get _template() {
        return `
        ${ESCHTML(this.modelName)}<br>
        <button class='btn btn-primary btn-sm' data-on="click:onopen">Open</button>`;
    }
}

class ModelInfo extends View {
    constructor(leafletMap, el) {
        super(el, 'div');
        this._leafletMap = leafletMap;
    }
    get model() { return this._model; }
    set model(model) {
        this._model = model;
        this._leafletMap.removeLayers();
        if(this._model !== null) {
            this._leafletMap.addLayer(this._getModelLayer(), 'model', true);
            this._leafletMap.fitBounds('model');
            this._childviews['loadHeatMapControl'] = new LoadHeatMapControl(this._leafletMap, this._model.name);
        }
        this.render();
    }
    _getModelLayer() {
        if(!this.model)
            throw "Can't get the model layer: No model given to ModelInfo";
        if(this.model.layerProm)
            return this.model.layerProm;
        let addNodePopup = (feature, layer) => {
            if(feature.geometry.type !== 'Point')
                return;
            layer.cyder_node_id = feature.properties.id;
            layer.on('click', (e) => { this._onNodeClick(e); });
        }
        return this.model.layerProm = createModelLayer(this.model.name, addNodePopup);
    }
    async _onNodeClick(e) {
        if(!e.target.getPopup()) {
            let node = await CyderAPI.Node.get(this.model.name, e.target.cyder_node_id);
            var display = (num) => (num == null) ? "NA" : ESCHTML(num);
            e.target.bindPopup(
                `Node ${ESCHTML(node.node_id)}<br>
                VoltageA: ${display(node.VA)}<br>
                VoltageB: ${display(node.VB)}<br>
                VoltageC: ${display(node.VC)}`);
            e.target.openPopup();
        }
    }

    get _template() {
        return `${ IF(this.model, () =>
            `<div class="row" style="margin-bottom: 1rem">
                <div class=col-lg-4>
                    <div class="card">
                        <div class="card-header">
                            Infos
                        </div>
                        <div class="card-body">
                            Model name: ${ ESCHTML(this.model.name) }<br>
                            Nodes count: <span id="nodescount"></span><br>
                            Devices count: <span id="devicescount"></span><br>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            Loads (kW)
                        </div>
                        <div id="" class="card-body">
                            <div data-childview="loadHeatMapControl"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header input-group">
                            <input class="form-control" placeholder="Search" name="srch-term" id="srch-term" type="text">
                            <div class="input-group-btn">
                                <button class="btn btn-default" type="submit">Search</button>
                            </div>
                        </div>
                        <div id="searchresult" class="card-body">
                            Search
                        </div>
                    </div>
                </div>
            </div>`
        ) }`;
    }
}

class LoadHeatMapControl extends View {
    constructor(leafletMap, modelname, el) {
        super(el, 'div');
        this._leafletMap = leafletMap;
        this._modelName = modelname;
        this._phases = new Set();
        this._layer = null;
        this.render();
    }
    async _onTooglePhase(e) {
        if(this._phases.has(e.target.dataset.phase)) {
            this._phases.delete(e.target.dataset.phase);
            e.target.classList.add('disabled');
        }
        else {
            this._phases.add(e.target.dataset.phase);
            e.target.classList.remove('disabled');
        }
        this._leafletMap.removeLayer("load");
        if(this._phases.size > 0) {
            this._layer = createLoadHeatmapLayer(this._modelName, this._phases);
            this._leafletMap.addLayer(this._layer, "load");
            this._layer = await this._layer;
            this._childviews['scale'] = new HeatMapScale(this._layer);
        }
        else {
            this._layer = null;
            this._childviews['scale'] = null;
        }
        this.render();
    }
    get _template() {
        return `
        <div class="btn-group btn-group-sm" role="group" style="display: flex; margin-bottom: 1em;">
            <button type="button" class="btn btn-secondary${IF(this._phases.has('A'), ()=> ' disabled')}" data-on="click:_onTooglePhase" data-phase="A" style="width: 33.3%;">Phase A</button>
            <button type="button" class="btn btn-secondary${IF(this._phases.has('B'), ()=> ' disabled')}" data-on="click:_onTooglePhase" data-phase="B" style="width: 33.3%;">Phase B</button>
            <button type="button" class="btn btn-secondary${IF(this._phases.has('C'), ()=> ' disabled')}" data-on="click:_onTooglePhase" data-phase="C" style="width: 33.3%;">Phase C</button>
        </div>
        ${ IF(this._layer !== null, () => `<div data-childview="scale"></div>`)}
        `;
    }
}

class HeatMapScale extends View {
    constructor(layer, el) {
        super(el, 'div');
        this._layer = layer;
        this.render();
    }
    _onMaxChange(e) {
        this._layer.setOptions({max: e.target.value});
    }
    get _template() {
        return `
        <div style="display: table;">
            <div>0 </div>
            <div style="display: table-cell; width: 100%; height: 1em; background: linear-gradient(to right, rgba(0,0,255,0.1), rgba(0,0,255,0.5), lime, yellow, red);"></div>
            <input style="display: table-cell; width:65px" data-on="change:_onMaxChange" type="number" value="${ this._layer.options.max }">
        </table>`;
    }
}
