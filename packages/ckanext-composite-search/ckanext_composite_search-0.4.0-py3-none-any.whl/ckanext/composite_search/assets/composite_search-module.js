ckan.module("composite-search", function ($) {
    "use strict";
    var EVENT_TOGGLE = "composite-search:toggle";
    var App = CompositeSearch.App;
    var stores = CompositeSearch.stores;

    return {
        options: {
            prefix: "ext_composite_",
            config: null,
            urlInit: false,
            enabled: false,
        },
        initialize: function () {
            var config = this.options.config || {};
            this.app = new App({
                target: this.el[0],
                props: {
                    definitions: config.definitions,
                    order: config.order
                },
            });
            stores.prefix.set(this.options.prefix);
            stores.formData.addDefault();

            this.sandbox.subscribe(EVENT_TOGGLE, this._onToggle);
            this.options.urlInit && this._initFromUrl();
            this.options.enabled && stores.state.enable();
        },
        teardown: function () {
            this.sandbox.unsubscribe(EVENT_TOGGLE, this._onToggle);
        },

        _initFromUrl: function () {
            var self = this;
            var stacks = window.location.search
                .slice(1)
                .split("&")
                .filter(function (str) {
                    return str.indexOf(self.options.prefix) === 0;
                }).map(function(str) {
                    var pair = str.trim().split('=');
                    return [pair[0].slice(self.options.prefix.length), pair[1]];
                }).reduce(function(data, pair){
                    if (!data[pair[0]]) {
                        data[pair[0]] = [];
                    }

                    // don't forget to handle spaces encoded as `+` instead of `%20`
                    data[pair[0]].push(decodeURIComponent(pair[1].replace(/\+/g, " ")));
                    return data;
                }, {});
            var keys = Object.keys(stacks);
            var longest = Math.max.apply(null, keys.map(function(k) { return stacks[k].length; }));
            var data = [];
            for (var i = 0; i < longest; ++i) {
                data.push(keys.reduce(function(record, key){
                    record[key] = stacks[key][i] || '';
                    return record;
                }, {}));
            }
            if (data.length) {
                stores.formData.set(data);
            }

        },
        _onToggle: function (state) {
            state ? stores.state.enable() : stores.state.disable();
        },
    };
});
