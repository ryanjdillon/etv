;
(function() {
    'use strict';

    function get_starting_map() {

      	//CartoDB layer names: light_all / dark_all / light_nonames / dark_nonames
        var baseURL = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'

        var base = L.tileLayer(baseURL, {
            attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ' });

        var map = L.map('map', {
            layers: [base],
            zoomControl: false
        }).setView([etvLat0, etvLon0], etvZoom);

        L.control.zoom({
            position: 'bottomright'
        }).addTo(map);
        map.scrollWheelZoom.disable();
        L.control.scale().addTo(map);

        // Don't show the 'Powered by Leaflet' text. Attribution overload
        var link_etv = "<a href='http://leafletjs.com/'>Leaflet</a>"
        var link_leaflet = "<a href='http://leafletjs.com/'>Leaflet</a>"
        map.attributionControl.setPrefix(link_leaflet+'|');
        return map;
    }


    var map = get_starting_map();

    var EtvApp = angular.module('EtvApp', ['mp.colorPicker']);


    // we do this to avoid conflict with Django interpolation
    // markers which also happen to be {{ and }}
    // now we redefined them to {[ ... ]}
    EtvApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
    });


    EtvApp.controller('EtvController', ['$scope', '$http', function(sc, http) {

        sc.time = 0;
        sc.legends = [];
        sc.overlays = {};
        sc.sections = etvSections;

        sc.speedOptions = [
            {id: 0, name: 1, speed: 1000},
            {id: 1, name: 2, speed: 500},
            {id: 2, name: 3, speed: 250},
            {id: 3, name: 4, speed: 125},
            {id: 4, name: 5, speed: 75}
        ];
        sc.speedIndex = '0';

        var colorScale = function(dataMin, dataMax, hexMin, hexMax) {
            return d3.scale.linear()
                .domain([dataMin, dataMax])
                .range([hexMin, hexMax]);
        }

        // Overlay constructor
        var Overlay = function(grid, s_name, p_name, d_name) {

            this.self = this;
            this.s_name = s_name;
            this.p_name = p_name;
            this.d_name = d_name;
            this.param_id = s_name + '_' + p_name + '_' + d_name;

            this.active = false;

            // Add transparent overlay for single parameter dimension to map
            this.add = function(grid, param_id) {
                var overlay = new L.d3SvgOverlay(function(sel, proj) {

                    var upd = sel.selectAll('path').data(grid);
                    upd.enter()
                        .append('path')
                        .attr('d', proj.pathFromGeojson)
                        .attr('stroke', 'transparent')
                        .attr('fill', 'transparent')
                        .attr('id', function(d) {
                            return param_id + '_' + d.id;
                        })
                        .attr('fill-opacity', '0.5');
                    upd.attr('stroke-width', 1 / proj.scale);
                });
                overlay.addTo(map);
            } // end add()

            // Query data via Etv API and set grid cell fill colors by value
            this.update = function() {
                var urlData = "/api/data/" + etvSimulationPath + "/";
                urlData += this.s_name + "/";
                urlData += this.p_name + "/";
                urlData += "time" + padd_with_zeros(sc.time, 4) + "/";
                urlData += this.d_name + "/";

                // fetch data and update layer
                var param_id = this.param_id;
                var hexMin = sc.sections[s_name]['parameters'][p_name]['colors'][0];
                var hexMax = sc.sections[s_name]['parameters'][p_name]['colors'][1];
                var valMin = sc.sections[s_name]['parameters'][p_name]['min'];
                var valMax = sc.sections[s_name]['parameters'][p_name]['max'];
                var scale = colorScale(valMin, valMax, hexMin, hexMax)

                http.get(urlData)
                    .success(function(data) {
                        d3.select(map.getPanes().overlayPane)
                            .selectAll("path[id^='" + param_id + "']")
                            .attr('fill', function(d) {
                                var c = null;
                                if (data[d.id] == null) {
                                    c = 'transparent';
                                    //c = scale(data[d.id]);
                                } else {
                                    c = scale(data[d.id]);
                                }
                                return c;
                            });
                    });
            } // end update()

            // Set grid cell fill colors to 'transparent'
            this.clear = function() {
                d3.select(map.getPanes().overlayPane)
                    .selectAll("path[id^='" + this.param_id + "']")
                    .attr('fill', 'transparent');
            } // end clear()

            // Initialize parameter/dim overlay
            this.add(grid, this.param_id)

        }; // end Overlay constructor


        // padds i with zeros to produce n-digit string
        function padd_with_zeros(x, n) {
            var xs = x.toString();
            if (xs.length < n) xs = Array(n + 1 - xs.length).join("0") + xs;
            return xs;
        } // end padd_with_zeros()


        // from parameters.yml we generate a d3 SVG overlay for each parameter
        // dimension with their respective GeoJSON FeatureCollection of grid
        // cell polygons
        for (var s_name in sc.sections) {
            if (sc.sections.hasOwnProperty(s_name)) {
                var s = sc.sections[s_name];
                var urlGrid = "/api/grid/" + etvSimulationPath + "/" + s_name + "/";
                http.get(urlGrid)
                    //.success(d3.json('grid.geo.json', function(data) {
                    .success(function(data) {
                        var grid = data.features;
                        for (var p_name in s['parameters']) {
                            if (sc.sections.hasOwnProperty(s_name)) {
                                var p = s['parameters'][p_name];

                                var d_base = p['dimension_name'];
                                var d_names = [];
                                d_names.push(p['reduction']);
                                for (var x = 0; x < p['layers'].length; x++) {
                                    var xs = String(x);
                                    d_names.push(d_base + padd_with_zeros(xs, 2));
                                }

                                for (var i = 0; i < d_names.length; i++) {
                                    var l = [s_name, p_name, d_names[i]];
                                    sc.overlays[l] = new Overlay(
                                        grid,
                                        s_name,
                                        p_name,
                                        d_names[i]);
                                } // end loop overlays
                            } // end if parameters
                        } // end loop parameters
                    }); // end success, http.get
            } // end if sections
        } // end for loop sections


        // http://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
        sc.hexToRgb = function(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? 'rgb(' + String(parseInt(result[1], 16)) +
                               ',' + String(parseInt(result[2], 16)) +
                               ',' + String(parseInt(result[3], 16)) + ')'
            : null;
        }

        // Update the legends array read by legends.html angular ng-repeat
        // legends is first an Object, then converted array once processed
        sc.updateLegends = function() {
            sc.legends = {};
            var active_found = false;
            for (var set in sc.overlays) {
                if (sc.overlays.hasOwnProperty(set)) {
                    var l = set.split(',');
                    var lset = [l[0], l[1]];
                    if (sc.overlays[l].active == true) {
                        sc.legends[lset] = lset;
                        active_found = true;
                    }
                }
            }
            if (active_found == true) {
                sc.legends = Object.keys(sc.legends).map(key => sc.legends[key]);
            } else {
                sc.legends = [];
            }
        };


//        // Add the geojson FeatureCollection of points
//        // The geojson is generated in the leaflet view and passed to the
//        // map.html template via the context where it is set to the JS variable
//        // `etvPoints`
//        function show_geojson_points() {
//            new L.GeoJSON(etvPoints).addTo(map);
//        };
//        show_geojson_points();
//
//        // Add the geojson polygons
//        // The list of geojson polygons is generated in the leaflet view and
//        // passed to the map.html template via the context where it is set to
//        // the JS variable `etvPolygons`, and the styles for each set in the JS
//        // variable `etvPolyStyles`
//        function show_geojson_polygons() {
//            for (var i = 0; i < etvPolys.length; i++) {
//                new L.GeoJSON(etvPolys[i], {
//                    style: etvPolyStyles[i]
//                }).addTo(map);
//            }
//        };
//        show_geojson_polygons();

        sc.showTimesteps = false;
        sc.timestep_to_calendar = {}

        http.get('/api/calendar/' + etvSimulationPath + '/')
            .success(function(data) {
                sc.timestep_to_calendar = data;
                sc.showTimesteps = true;
            })

        // Concatenate d_name from section & parameter names and dimension index
        sc.intTodName = function(s_name, p_name, x) {
            var xs = String(x);
            var d_name = null;

            if (xs == 'all') {
                d_name = sc.sections[s_name]['parameters'][p_name]['reduction'];
            } else {
                d_name = sc.sections[s_name]['parameters'][p_name]['dimension_name'];
                d_name = d_name + padd_with_zeros(xs, 2);
            }

            return d_name;
        }


        // Retrieve overly `param_id` from dimension index
        // called in `parameters.html` template
        sc.getParamId = function(s_name, p_name, x) {
            var d_name = sc.intTodName(s_name, p_name, x);
            return s_name+'_'+p_name+'_'+d_name
        }


        // Parse dimension index from d_name
        sc.dNameToInt = function(d_name) {
            return parseInt(d_name.replace(/[-+()\s]/g, ''));
        }


        // Toggle visibility of overlay
        sc.click = function(s_name, p_name, x) {
            var d_name = sc.intTodName(s_name, p_name, x);
            var overlay = sc.overlays[[s_name, p_name, d_name]];
            if (overlay.active == false) {
                overlay.update();
                overlay.active = true;
            } else {
                overlay.clear();
                overlay.active = false;
            }
            sc.updateLegends();
        };


        // Return CSS suffix for overlay's active status
        // called in `parameters.html` template
        sc.getButtonStyle = function(s_name, p_name, x) {
            var d_name = sc.intTodName(s_name, p_name, x);
            var overlay = sc.overlays[[s_name, p_name, d_name]];
            if(typeof overlay !== 'undefined') {
                if (overlay.active == true) {
                    return 'active';
                } else {
                    return 'inactive';
                }
            }
            else {
                return 'inactive';
            }
        };


        // Update all active overlays
        sc.update_overlays_all = function() {
            for (var set in sc.overlays) {
                if (sc.overlays.hasOwnProperty(set)) {
                    var l = set.split(',');
                    if (sc.overlays[l].active == true) {
                        sc.overlays[l].update();
                    }
                }
            }
        };


        // Update all active overlays for a given parameter
        sc.update_parameter = function(s_name, p_name) {
            for (var set in sc.overlays) {
                if (sc.overlays.hasOwnProperty(set)) {
                    var l = set.split(',');
                    if ((s_name == l[0]) && (p_name == l[1])) {
                        if (sc.overlays[l].active == true) {
                            sc.overlays[l].update();
                        }
                    }
                }
            }
        };


        function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        }

        // Clears all parameters
        sc.clearAllSelections = async function() {
            // Clear overlay fill color, update button CSS
            for (var set in sc.overlays) {
                if (sc.overlays.hasOwnProperty(set)) {
                    var l = set.split(',');
                    sc.overlays[l].clear();
                    sc.overlays[l].active = false;
                    // Update CSS class for elements
                    var elemId = l.join('_');
                    var elem = document.getElementById(elemId);
                    elem.setAttribute('class', 'block-item layer-btn inactive');
                }
            }
            // Update section CSS
            for (var s_name in sc.sections) {
                var elem = document.getElementById('section_'+s_name);
                elem.setAttribute('class', 'list-group-item strong inactive');
            }

            sc.updateLegends();
        };


        // Change section header CSS if child overlays selected
        sc.getListGroupColor = function(s_name) {
            var i = 0;

            for (var set in sc.overlays) {
                if (sc.overlays.hasOwnProperty(set)) {
                    var l = set.split(',');
                    if (l[0] == s_name) {
                        if (sc.overlays[l].active == true) {
                            i += 1;
                        }
                    }
                }
            }

            if (i > 0) {
                return 'active';
            } else {
                return 'inactive';
            }
        };


        // Propagate time and update all active layers
        sc.moveTime = function(dt) {
            // prevent jumping outside of bounds
            if (sc.time + dt in sc.timestep_to_calendar) {
                sc.time += dt;
                sc.update_overlays_all();
            }
        };

        function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        }

        sc.play = async function() {
            while (sc.time + 1 in sc.timestep_to_calendar) {
                console.log('play time-step: '+String(sc.time));
                sc.moveTime(1);
                await sleep(sc.speedOptions[sc.speedIndex].speed);
            }
        };

        // Reset time and update all active layers
        sc.resetTime = function() {
            sc.time = 0;
            sc.update_overlays_all();
        };


        // Get datetime string for current timestep
        sc.getTime = function() {
            return sc.timestep_to_calendar[parseInt(sc.time)];
        };

    }]);

})();
