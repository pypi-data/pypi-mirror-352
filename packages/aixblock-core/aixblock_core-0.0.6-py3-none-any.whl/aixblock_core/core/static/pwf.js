/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 909:
/***/ ((module, exports, __webpack_require__) => {

    var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__, exports, __webpack_require__(322)], __WEBPACK_AMD_DEFINE_RESULT__ = (function (require, exports, tslib_1) {
        "use strict";
        Object.defineProperty(exports, "__esModule", ({ value: true }));
        exports._PWF_MANAGED_TOKEN_LOCAL_STORAGE_KEY = exports._PWF_JWT_TOKEN_QUERY_PARAM_NAME = exports.$$VEventName = exports.NEW_CONNECTION_QUERY_PARAMS = exports.$$CEventName = void 0;
        var $$CEventName;
        (function ($$CEventName) {
            $$CEventName["CLIENT_INIT"] = "CLIENT_INIT";
            $$CEventName["CLIENT_ROUTE_CHANGED"] = "CLIENT_ROUTE_CHANGED";
            $$CEventName["CLIENT_NEW_CONNECTION_DIALOG_CLOSED"] = "CLIENT_NEW_CONNECTION_DIALOG_CLOSED";
            $$CEventName["CLIENT_SHOW_CONNECTION_IFRAME"] = "CLIENT_SHOW_CONNECTION_IFRAME";
            $$CEventName["CLIENT_CONNECTION_NAME_IS_INVALID"] = "CLIENT_CONNECTION_NAME_IS_INVALID";
            $$CEventName["CLIENT_AUTHENTICATION_SUCCESS"] = "CLIENT_AUTHENTICATION_SUCCESS";
            $$CEventName["CLIENT_AUTHENTICATION_FAILED"] = "CLIENT_AUTHENTICATION_FAILED";
            $$CEventName["CLIENT_CONFIGURATION_FINISHED"] = "CLIENT_CONFIGURATION_FINISHED";
            $$CEventName["CLIENT_CONNECTION_PIECE_NOT_FOUND"] = "CLIENT_CONNECTION_PIECE_NOT_FOUND";
        })($$CEventName || (exports.$$CEventName = $$CEventName = {}));
        exports.NEW_CONNECTION_QUERY_PARAMS = {
            name: 'pieceName',
            connectionName: 'connectionName',
            randomId: 'randomId'
        };
        var $$VEventName;
        (function ($$VEventName) {
            $$VEventName["VENDOR_INIT"] = "VENDOR_INIT";
            $$VEventName["VENDOR_ROUTE_CHANGED"] = "VENDOR_ROUTE_CHANGED";
        })($$VEventName || (exports.$$VEventName = $$VEventName = {}));
        // We used to send JWT in query params, now we send it in local storage
        exports._PWF_JWT_TOKEN_QUERY_PARAM_NAME = "jwtToken";
        exports._PWF_MANAGED_TOKEN_LOCAL_STORAGE_KEY = "pwf_managed_token";
        class Workflow {
            constructor() {
                this._sdkVersion = "1.0.0";
                this._prefix = '';
                this._instanceUrl = '';
                this._hideSidebar = false;
                this._hideFolders = false;
                this._hideLogoInBuilder = false;
                this._hideFlowNameInBuilder = false;
                this._jwtToken = '';
                this._disableNavigationInBuilder = true;
                this._parentOrigin = window.location.origin;
                this._MAX_CONTAINER_CHECK_COUNT = 100;
                this._HUNDRED_MILLISECONDS = 100;
                this._initializeBuilderAndDashboardIframe = ({ containerSelector }) => {
                    return new Promise((resolve, reject) => {
                        this._addGracePeriodBeforeMethod({
                            condition: () => {
                                return !!document.querySelector(containerSelector);
                            },
                            method: () => {
                                const iframeContainer = document.querySelector(containerSelector);
                                if (iframeContainer) {
                                    const iframeWindow = this.connectToEmbed({
                                        iframeContainer,
                                        callbackAfterConfigurationFinished: () => {
                                            resolve({ status: "success" });
                                        },
                                        initialRoute: '/'
                                    }).contentWindow;
                                    this._dashboardAndBuilderIframeWindow = iframeWindow;
                                    this._checkForClientRouteChanges(iframeWindow);
                                }
                                else {
                                    reject({
                                        status: "error",
                                        error: {
                                            message: 'container not found',
                                        },
                                    });
                                }
                            },
                            errorMessage: 'container not found',
                        });
                    });
                };
                this._createConfigurationFinishedListener = (targetWindow, callbackAfterConfigurationFinished) => {
                    const configurationFinishedHandler = (event) => {
                        if (event.data.type === $$CEventName.CLIENT_CONFIGURATION_FINISHED && event.source === targetWindow) {
                            this._logger().log('Configuration finished');
                            if (callbackAfterConfigurationFinished) {
                                callbackAfterConfigurationFinished();
                            }
                        }
                    };
                    window.addEventListener('message', configurationFinishedHandler);
                };
                this._createAuthenticationFailedListener = (targetWindow) => {
                    const authenticationFailedHandler = (event) => {
                        if (event.data.type === $$CEventName.CLIENT_AUTHENTICATION_FAILED && event.source === targetWindow) {
                            this._errorCreator('Authentication failed', event.data.data);
                        }
                    };
                    window.addEventListener('message', authenticationFailedHandler);
                };
                this._createAuthenticationSuccessListener = (targetWindow) => {
                    const authenticationSuccessHandler = (event) => {
                        if (event.data.type === $$CEventName.CLIENT_AUTHENTICATION_SUCCESS && event.source === targetWindow) {
                            this._logger().log('Authentication success');
                            window.removeEventListener('message', authenticationSuccessHandler);
                        }
                    };
                    window.addEventListener('message', authenticationSuccessHandler);
                };
                this._checkForClientRouteChanges = (source) => {
                    window.addEventListener('message', (event) => {
                        if (event.data.type ===
                            $$CEventName.CLIENT_ROUTE_CHANGED &&
                            event.source === source) {
                            let prefixStartsWithSlash = this._prefix.startsWith('/')
                                ? this._prefix
                                : `/${this._prefix}`;
                            if (prefixStartsWithSlash === '/') {
                                prefixStartsWithSlash = '';
                            }
                            let routeWithPrefix = prefixStartsWithSlash + event.data.data.route;
                            if (!routeWithPrefix.startsWith('/')) {
                                routeWithPrefix = '/' + routeWithPrefix;
                            }
                            if (this._navigationHandler) {
                                this._navigationHandler({ route: routeWithPrefix });
                            }
                        }
                    });
                };
                // eslint-disable-next-line @typescript-eslint/no-empty-function
                this._cleanConnectionIframe = () => { };
            }
            configure({ prefix, jwtToken, instanceUrl, embedding, }) {
                var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l;
                this._prefix = prefix || '/';
                this._hideSidebar = ((_a = embedding === null || embedding === void 0 ? void 0 : embedding.dashboard) === null || _a === void 0 ? void 0 : _a.hideSidebar) || false;
                this._instanceUrl = this._removeTrailingSlashes(instanceUrl);
                this._disableNavigationInBuilder =
                    (_c = (_b = embedding === null || embedding === void 0 ? void 0 : embedding.builder) === null || _b === void 0 ? void 0 : _b.disableNavigation) !== null && _c !== void 0 ? _c : false;
                this._hideFolders = (_d = embedding === null || embedding === void 0 ? void 0 : embedding.hideFolders) !== null && _d !== void 0 ? _d : false;
                this._hideLogoInBuilder = (_f = (_e = embedding === null || embedding === void 0 ? void 0 : embedding.builder) === null || _e === void 0 ? void 0 : _e.hideLogo) !== null && _f !== void 0 ? _f : false;
                this._hideFlowNameInBuilder = (_h = (_g = embedding === null || embedding === void 0 ? void 0 : embedding.builder) === null || _g === void 0 ? void 0 : _g.hideFlowName) !== null && _h !== void 0 ? _h : false;
                this._jwtToken = jwtToken;
                this._fontUrl = (_j = embedding === null || embedding === void 0 ? void 0 : embedding.styling) === null || _j === void 0 ? void 0 : _j.fontUrl;
                this._fontFamily = (_k = embedding === null || embedding === void 0 ? void 0 : embedding.styling) === null || _k === void 0 ? void 0 : _k.fontFamily;
                this._navigationHandler = (_l = embedding === null || embedding === void 0 ? void 0 : embedding.navigation) === null || _l === void 0 ? void 0 : _l.handler;
                if (embedding === null || embedding === void 0 ? void 0 : embedding.containerId) {
                    return this._initializeBuilderAndDashboardIframe({
                        containerSelector: `#${embedding.containerId}`
                    });
                }
                return new Promise((resolve) => { resolve({ status: "success" }); });
            }
            _setupInitialMessageHandler(targetWindow, initialRoute, callbackAfterConfigurationFinished) {
                const initialMessageHandler = (event) => {
                    if (event.source === targetWindow) {
                        switch (event.data.type) {
                            case $$CEventName.CLIENT_INIT: {
                                const apEvent = {
                                    type: $$VEventName.VENDOR_INIT,
                                    data: {
                                        prefix: this._prefix,
                                        hideSidebar: this._hideSidebar,
                                        disableNavigationInBuilder: this._disableNavigationInBuilder,
                                        hideFolders: this._hideFolders,
                                        hideLogoInBuilder: this._hideLogoInBuilder,
                                        hideFlowNameInBuilder: this._hideFlowNameInBuilder,
                                        jwtToken: this._jwtToken,
                                        initialRoute,
                                        fontUrl: this._fontUrl,
                                        fontFamily: this._fontFamily,
                                    },
                                };
                                targetWindow.postMessage(apEvent, '*');
                                this._createAuthenticationSuccessListener(targetWindow);
                                this._createAuthenticationFailedListener(targetWindow);
                                this._createConfigurationFinishedListener(targetWindow, callbackAfterConfigurationFinished);
                                window.removeEventListener('message', initialMessageHandler);
                                break;
                            }
                        }
                    }
                };
                window.addEventListener('message', initialMessageHandler);
            }
            connectToEmbed({ iframeContainer, initialRoute, callbackAfterConfigurationFinished }) {
                const iframe = this._createIframe({ src: `${this._instanceUrl}/embed` });
                iframeContainer.appendChild(iframe);
                if (!this._doesFrameHaveWindow(iframe)) {
                    this._errorCreator('iframe window not accessible');
                }
                const iframeWindow = iframe.contentWindow;
                this._setupInitialMessageHandler(iframeWindow, initialRoute, callbackAfterConfigurationFinished);
                return iframe;
            }
            _createIframe({ src }) {
                const iframe = document.createElement('iframe');
                iframe.src = src;
                iframe.setAttribute('allow', 'clipboard-read; clipboard-write');
                return iframe;
            }
            _getNewWindowFeatures(requestedFeats) {
                const windowFeats = {
                    height: 700,
                    width: 700,
                    top: 0,
                    left: 0,
                };
                Object.keys(windowFeats).forEach((key) => {
                    if (typeof requestedFeats === 'object' && requestedFeats[key]) {
                        windowFeats[key] = requestedFeats[key];
                    }
                });
                return `width=${windowFeats.width},height=${windowFeats.height},top=${windowFeats.top},left=${windowFeats.left}`;
            }
            _addConnectionIframe({ pieceName, connectionName }) {
                const connectionsIframe = this.connectToEmbed({
                    iframeContainer: document.body,
                    initialRoute: `/embed/connections?${exports.NEW_CONNECTION_QUERY_PARAMS.name}=${pieceName}&randomId=${Date.now()}&${exports.NEW_CONNECTION_QUERY_PARAMS.connectionName}=${connectionName || ''}`
                });
                connectionsIframe.style.cssText = ['display:none', 'position:fixed', 'top:0', 'left:0', 'width:100%', 'height:100%', 'border:none'].join(';');
                return connectionsIframe;
            }
            _openNewWindowForConnections({ pieceName, connectionName, newWindow }) {
                const popup = window.open(`${this._instanceUrl}/embed`, '_blank', this._getNewWindowFeatures(newWindow));
                if (!popup) {
                    this._errorCreator('Failed to open popup window');
                }
                this._setupInitialMessageHandler(popup, `/embed/connections?${exports.NEW_CONNECTION_QUERY_PARAMS.name}=${pieceName}&randomId=${Date.now()}&${exports.NEW_CONNECTION_QUERY_PARAMS.connectionName}=${connectionName || ''}`);
                return popup;
            }
            connect(_a) {
                return tslib_1.__awaiter(this, arguments, void 0, function* ({ pieceName, connectionName, newWindow }) {
                    this._cleanConnectionIframe();
                    return this._addGracePeriodBeforeMethod({
                        condition: () => {
                            return !!document.body;
                        },
                        method: () => tslib_1.__awaiter(this, void 0, void 0, function* () {
                            const target = newWindow ? this._openNewWindowForConnections({ pieceName, connectionName, newWindow }) : this._addConnectionIframe({ pieceName, connectionName });
                            //don't check for window because (instanceof Window) is false for popups
                            if (!(target instanceof HTMLIFrameElement)) {
                                const checkClosed = setInterval(() => {
                                    if (target.closed) {
                                        clearInterval(checkClosed);
                                        if (this._resolveNewConnectionDialogClosed) {
                                            this._resolveNewConnectionDialogClosed({ connection: undefined });
                                        }
                                    }
                                }, 500);
                            }
                            return new Promise((resolve, reject) => {
                                this._resolveNewConnectionDialogClosed = resolve;
                                this._rejectNewConnectionDialogClosed = reject;
                                this._setConnectionIframeEventsListener(target);
                            });
                        }),
                        errorMessage: 'unable to add connection embedding'
                    });
                });
            }
            navigate({ route }) {
                if (!this._dashboardAndBuilderIframeWindow) {
                    this._logger().error('dashboard iframe not found');
                    return;
                }
                const event = {
                    type: $$VEventName.VENDOR_ROUTE_CHANGED,
                    data: {
                        vendorRoute: route,
                    },
                };
                this._dashboardAndBuilderIframeWindow.postMessage(event, '*');
            }
            _extractRouteAfterPrefix(href, prefix) {
                return href.split(prefix)[1];
            }
            _doesFrameHaveWindow(frame) {
                return frame.contentWindow !== null;
            }
            _setConnectionIframeEventsListener(target) {
                const connectionRelatedMessageHandler = (event) => {
                    if (event.data.type) {
                        switch (event.data.type) {
                            case $$CEventName.CLIENT_NEW_CONNECTION_DIALOG_CLOSED: {
                                if (this._resolveNewConnectionDialogClosed) {
                                    this._resolveNewConnectionDialogClosed(event.data.data);
                                }
                                this._removeEmbedding(target);
                                window.removeEventListener('message', connectionRelatedMessageHandler);
                                break;
                            }
                            case $$CEventName.CLIENT_CONNECTION_NAME_IS_INVALID:
                            case $$CEventName.CLIENT_CONNECTION_PIECE_NOT_FOUND: {
                                this._removeEmbedding(target);
                                if (this._rejectNewConnectionDialogClosed) {
                                    this._rejectNewConnectionDialogClosed(event.data.data);
                                }
                                else {
                                    this._errorCreator(event.data.data.error);
                                }
                                window.removeEventListener('message', connectionRelatedMessageHandler);
                                break;
                            }
                            case $$CEventName.CLIENT_SHOW_CONNECTION_IFRAME: {
                                if (target instanceof HTMLIFrameElement) {
                                    target.style.display = 'block';
                                }
                                break;
                            }
                        }
                    }
                };
                window.addEventListener('message', connectionRelatedMessageHandler);
                this._cleanConnectionIframe = () => {
                    window.removeEventListener('message', connectionRelatedMessageHandler);
                    this._resolveNewConnectionDialogClosed = undefined;
                    this._rejectNewConnectionDialogClosed = undefined;
                    this._removeEmbedding(target);
                };
            }
            _removeTrailingSlashes(str) {
                return str.endsWith('/') ? str.slice(0, -1) : str;
            }
            /**Adds a grace period before executing the method depending on the condition */
            _addGracePeriodBeforeMethod({ method, condition, errorMessage, }) {
                return new Promise((resolve, reject) => {
                    let checkCounter = 0;
                    if (condition()) {
                        resolve(method());
                        return;
                    }
                    const checker = setInterval(() => {
                        if (checkCounter >= this._MAX_CONTAINER_CHECK_COUNT) {
                            this._logger().error(errorMessage);
                            reject(errorMessage);
                            return;
                        }
                        checkCounter++;
                        if (condition()) {
                            clearInterval(checker);
                            resolve(method());
                        }
                    }, this._HUNDRED_MILLISECONDS);
                });
            }
            extractActivepiecesRouteFromUrl({ vendorUrl }) {
                const prefixStartsWithSlash = this._prefix.startsWith('/');
                return this._extractRouteAfterPrefix(vendorUrl, prefixStartsWithSlash
                    ? this._parentOrigin + this._prefix
                    : `${this._parentOrigin}/${this._prefix}`);
            }
            _errorCreator(message, ...args) {
                this._logger().error(message, ...args);
                throw new Error(`Workflow: ${message}`);
            }
            _removeEmbedding(target) {
                if (target) {
                    if (target instanceof HTMLIFrameElement) {
                        target.remove();
                    }
                    else {
                        target.close();
                    }
                }
                else {
                    this._logger().warn(`couldn't remove embedding`);
                }
            }
            _logger() {
                return {
                    log: (message, ...args) => {
                        console.log(`Workflow: ${message}`, ...args);
                    },
                    error: (message, ...args) => {
                        console.error(`Workflow: ${message}`, ...args);
                    },
                    warn: (message, ...args) => {
                        console.warn(`Workflow: ${message}`, ...args);
                    }
                };
            }
        }
        window.pwf = new Workflow();
        window.Workflow = Workflow;
    }).apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
            __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
    
    
    /***/ }),
    
    /***/ 322:
    /***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {
    
    "use strict";
    __webpack_require__.r(__webpack_exports__);
    /* harmony export */ __webpack_require__.d(__webpack_exports__, {
    /* harmony export */   __addDisposableResource: () => (/* binding */ __addDisposableResource),
    /* harmony export */   __assign: () => (/* binding */ __assign),
    /* harmony export */   __asyncDelegator: () => (/* binding */ __asyncDelegator),
    /* harmony export */   __asyncGenerator: () => (/* binding */ __asyncGenerator),
    /* harmony export */   __asyncValues: () => (/* binding */ __asyncValues),
    /* harmony export */   __await: () => (/* binding */ __await),
    /* harmony export */   __awaiter: () => (/* binding */ __awaiter),
    /* harmony export */   __classPrivateFieldGet: () => (/* binding */ __classPrivateFieldGet),
    /* harmony export */   __classPrivateFieldIn: () => (/* binding */ __classPrivateFieldIn),
    /* harmony export */   __classPrivateFieldSet: () => (/* binding */ __classPrivateFieldSet),
    /* harmony export */   __createBinding: () => (/* binding */ __createBinding),
    /* harmony export */   __decorate: () => (/* binding */ __decorate),
    /* harmony export */   __disposeResources: () => (/* binding */ __disposeResources),
    /* harmony export */   __esDecorate: () => (/* binding */ __esDecorate),
    /* harmony export */   __exportStar: () => (/* binding */ __exportStar),
    /* harmony export */   __extends: () => (/* binding */ __extends),
    /* harmony export */   __generator: () => (/* binding */ __generator),
    /* harmony export */   __importDefault: () => (/* binding */ __importDefault),
    /* harmony export */   __importStar: () => (/* binding */ __importStar),
    /* harmony export */   __makeTemplateObject: () => (/* binding */ __makeTemplateObject),
    /* harmony export */   __metadata: () => (/* binding */ __metadata),
    /* harmony export */   __param: () => (/* binding */ __param),
    /* harmony export */   __propKey: () => (/* binding */ __propKey),
    /* harmony export */   __read: () => (/* binding */ __read),
    /* harmony export */   __rest: () => (/* binding */ __rest),
    /* harmony export */   __runInitializers: () => (/* binding */ __runInitializers),
    /* harmony export */   __setFunctionName: () => (/* binding */ __setFunctionName),
    /* harmony export */   __spread: () => (/* binding */ __spread),
    /* harmony export */   __spreadArray: () => (/* binding */ __spreadArray),
    /* harmony export */   __spreadArrays: () => (/* binding */ __spreadArrays),
    /* harmony export */   __values: () => (/* binding */ __values),
    /* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
    /* harmony export */ });
    /******************************************************************************
    Copyright (c) Microsoft Corporation.
    
    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted.
    
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
    REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
    INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
    LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
    OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    PERFORMANCE OF THIS SOFTWARE.
    ***************************************************************************** */
    /* global Reflect, Promise, SuppressedError, Symbol */
    
    var extendStatics = function(d, b) {
      extendStatics = Object.setPrototypeOf ||
          ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
          function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
      return extendStatics(d, b);
    };
    
    function __extends(d, b) {
      if (typeof b !== "function" && b !== null)
          throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
      extendStatics(d, b);
      function __() { this.constructor = d; }
      d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    }
    
    var __assign = function() {
      __assign = Object.assign || function __assign(t) {
          for (var s, i = 1, n = arguments.length; i < n; i++) {
              s = arguments[i];
              for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
          }
          return t;
      }
      return __assign.apply(this, arguments);
    }
    
    function __rest(s, e) {
      var t = {};
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
          t[p] = s[p];
      if (s != null && typeof Object.getOwnPropertySymbols === "function")
          for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
              if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                  t[p[i]] = s[p[i]];
          }
      return t;
    }
    
    function __decorate(decorators, target, key, desc) {
      var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
      if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
      else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
      return c > 3 && r && Object.defineProperty(target, key, r), r;
    }
    
    function __param(paramIndex, decorator) {
      return function (target, key) { decorator(target, key, paramIndex); }
    }
    
    function __esDecorate(ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
      function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
      var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
      var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
      var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
      var _, done = false;
      for (var i = decorators.length - 1; i >= 0; i--) {
          var context = {};
          for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
          for (var p in contextIn.access) context.access[p] = contextIn.access[p];
          context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
          var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
          if (kind === "accessor") {
              if (result === void 0) continue;
              if (result === null || typeof result !== "object") throw new TypeError("Object expected");
              if (_ = accept(result.get)) descriptor.get = _;
              if (_ = accept(result.set)) descriptor.set = _;
              if (_ = accept(result.init)) initializers.unshift(_);
          }
          else if (_ = accept(result)) {
              if (kind === "field") initializers.unshift(_);
              else descriptor[key] = _;
          }
      }
      if (target) Object.defineProperty(target, contextIn.name, descriptor);
      done = true;
    };
    
    function __runInitializers(thisArg, initializers, value) {
      var useValue = arguments.length > 2;
      for (var i = 0; i < initializers.length; i++) {
          value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
      }
      return useValue ? value : void 0;
    };
    
    function __propKey(x) {
      return typeof x === "symbol" ? x : "".concat(x);
    };
    
    function __setFunctionName(f, name, prefix) {
      if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
      return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
    };
    
    function __metadata(metadataKey, metadataValue) {
      if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(metadataKey, metadataValue);
    }
    
    function __awaiter(thisArg, _arguments, P, generator) {
      function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
      return new (P || (P = Promise))(function (resolve, reject) {
          function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
          function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
          function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
          step((generator = generator.apply(thisArg, _arguments || [])).next());
      });
    }
    
    function __generator(thisArg, body) {
      var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
      return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
      function verb(n) { return function (v) { return step([n, v]); }; }
      function step(op) {
          if (f) throw new TypeError("Generator is already executing.");
          while (g && (g = 0, op[0] && (_ = 0)), _) try {
              if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
              if (y = 0, t) op = [op[0] & 2, t.value];
              switch (op[0]) {
                  case 0: case 1: t = op; break;
                  case 4: _.label++; return { value: op[1], done: false };
                  case 5: _.label++; y = op[1]; op = [0]; continue;
                  case 7: op = _.ops.pop(); _.trys.pop(); continue;
                  default:
                      if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                      if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                      if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                      if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                      if (t[2]) _.ops.pop();
                      _.trys.pop(); continue;
              }
              op = body.call(thisArg, _);
          } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
          if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
      }
    }
    
    var __createBinding = Object.create ? (function(o, m, k, k2) {
      if (k2 === undefined) k2 = k;
      var desc = Object.getOwnPropertyDescriptor(m, k);
      if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
          desc = { enumerable: true, get: function() { return m[k]; } };
      }
      Object.defineProperty(o, k2, desc);
    }) : (function(o, m, k, k2) {
      if (k2 === undefined) k2 = k;
      o[k2] = m[k];
    });
    
    function __exportStar(m, o) {
      for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(o, p)) __createBinding(o, m, p);
    }
    
    function __values(o) {
      var s = typeof Symbol === "function" && Symbol.iterator, m = s && o[s], i = 0;
      if (m) return m.call(o);
      if (o && typeof o.length === "number") return {
          next: function () {
              if (o && i >= o.length) o = void 0;
              return { value: o && o[i++], done: !o };
          }
      };
      throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
    }
    
    function __read(o, n) {
      var m = typeof Symbol === "function" && o[Symbol.iterator];
      if (!m) return o;
      var i = m.call(o), r, ar = [], e;
      try {
          while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
      }
      catch (error) { e = { error: error }; }
      finally {
          try {
              if (r && !r.done && (m = i["return"])) m.call(i);
          }
          finally { if (e) throw e.error; }
      }
      return ar;
    }
    
    /** @deprecated */
    function __spread() {
      for (var ar = [], i = 0; i < arguments.length; i++)
          ar = ar.concat(__read(arguments[i]));
      return ar;
    }
    
    /** @deprecated */
    function __spreadArrays() {
      for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
      for (var r = Array(s), k = 0, i = 0; i < il; i++)
          for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
              r[k] = a[j];
      return r;
    }
    
    function __spreadArray(to, from, pack) {
      if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
          if (ar || !(i in from)) {
              if (!ar) ar = Array.prototype.slice.call(from, 0, i);
              ar[i] = from[i];
          }
      }
      return to.concat(ar || Array.prototype.slice.call(from));
    }
    
    function __await(v) {
      return this instanceof __await ? (this.v = v, this) : new __await(v);
    }
    
    function __asyncGenerator(thisArg, _arguments, generator) {
      if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
      var g = generator.apply(thisArg, _arguments || []), i, q = [];
      return i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i;
      function verb(n) { if (g[n]) i[n] = function (v) { return new Promise(function (a, b) { q.push([n, v, a, b]) > 1 || resume(n, v); }); }; }
      function resume(n, v) { try { step(g[n](v)); } catch (e) { settle(q[0][3], e); } }
      function step(r) { r.value instanceof __await ? Promise.resolve(r.value.v).then(fulfill, reject) : settle(q[0][2], r); }
      function fulfill(value) { resume("next", value); }
      function reject(value) { resume("throw", value); }
      function settle(f, v) { if (f(v), q.shift(), q.length) resume(q[0][0], q[0][1]); }
    }
    
    function __asyncDelegator(o) {
      var i, p;
      return i = {}, verb("next"), verb("throw", function (e) { throw e; }), verb("return"), i[Symbol.iterator] = function () { return this; }, i;
      function verb(n, f) { i[n] = o[n] ? function (v) { return (p = !p) ? { value: __await(o[n](v)), done: false } : f ? f(v) : v; } : f; }
    }
    
    function __asyncValues(o) {
      if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
      var m = o[Symbol.asyncIterator], i;
      return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
      function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
      function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
    }
    
    function __makeTemplateObject(cooked, raw) {
      if (Object.defineProperty) { Object.defineProperty(cooked, "raw", { value: raw }); } else { cooked.raw = raw; }
      return cooked;
    };
    
    var __setModuleDefault = Object.create ? (function(o, v) {
      Object.defineProperty(o, "default", { enumerable: true, value: v });
    }) : function(o, v) {
      o["default"] = v;
    };
    
    function __importStar(mod) {
      if (mod && mod.__esModule) return mod;
      var result = {};
      if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
      __setModuleDefault(result, mod);
      return result;
    }
    
    function __importDefault(mod) {
      return (mod && mod.__esModule) ? mod : { default: mod };
    }
    
    function __classPrivateFieldGet(receiver, state, kind, f) {
      if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
      if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
      return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
    }
    
    function __classPrivateFieldSet(receiver, state, value, kind, f) {
      if (kind === "m") throw new TypeError("Private method is not writable");
      if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
      if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
    }
    
    function __classPrivateFieldIn(state, receiver) {
      if (receiver === null || (typeof receiver !== "object" && typeof receiver !== "function")) throw new TypeError("Cannot use 'in' operator on non-object");
      return typeof state === "function" ? receiver === state : state.has(receiver);
    }
    
    function __addDisposableResource(env, value, async) {
      if (value !== null && value !== void 0) {
        if (typeof value !== "object" && typeof value !== "function") throw new TypeError("Object expected.");
        var dispose;
        if (async) {
            if (!Symbol.asyncDispose) throw new TypeError("Symbol.asyncDispose is not defined.");
            dispose = value[Symbol.asyncDispose];
        }
        if (dispose === void 0) {
            if (!Symbol.dispose) throw new TypeError("Symbol.dispose is not defined.");
            dispose = value[Symbol.dispose];
        }
        if (typeof dispose !== "function") throw new TypeError("Object not disposable.");
        env.stack.push({ value: value, dispose: dispose, async: async });
      }
      else if (async) {
        env.stack.push({ async: true });
      }
      return value;
    }
    
    var _SuppressedError = typeof SuppressedError === "function" ? SuppressedError : function (error, suppressed, message) {
      var e = new Error(message);
      return e.name = "SuppressedError", e.error = error, e.suppressed = suppressed, e;
    };
    
    function __disposeResources(env) {
      function fail(e) {
        env.error = env.hasError ? new _SuppressedError(e, env.error, "An error was suppressed during disposal.") : e;
        env.hasError = true;
      }
      function next() {
        while (env.stack.length) {
          var rec = env.stack.pop();
          try {
            var result = rec.dispose && rec.dispose.call(rec.value);
            if (rec.async) return Promise.resolve(result).then(next, function(e) { fail(e); return next(); });
          }
          catch (e) {
              fail(e);
          }
        }
        if (env.hasError) throw env.error;
      }
      return next();
    }
    
    /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
      __extends,
      __assign,
      __rest,
      __decorate,
      __param,
      __metadata,
      __awaiter,
      __generator,
      __createBinding,
      __exportStar,
      __values,
      __read,
      __spread,
      __spreadArrays,
      __spreadArray,
      __await,
      __asyncGenerator,
      __asyncDelegator,
      __asyncValues,
      __makeTemplateObject,
      __importStar,
      __importDefault,
      __classPrivateFieldGet,
      __classPrivateFieldSet,
      __classPrivateFieldIn,
      __addDisposableResource,
      __disposeResources,
    });
    
    
    /***/ })
    
    /******/ 	});
    /************************************************************************/
    /******/ 	// The module cache
    /******/ 	var __webpack_module_cache__ = {};
    /******/ 	
    /******/ 	// The require function
    /******/ 	function __webpack_require__(moduleId) {
    /******/ 		// Check if module is in cache
    /******/ 		var cachedModule = __webpack_module_cache__[moduleId];
    /******/ 		if (cachedModule !== undefined) {
    /******/ 			return cachedModule.exports;
    /******/ 		}
    /******/ 		// Create a new module (and put it into the cache)
    /******/ 		var module = __webpack_module_cache__[moduleId] = {
    /******/ 			// no module.id needed
    /******/ 			// no module.loaded needed
    /******/ 			exports: {}
    /******/ 		};
    /******/ 	
    /******/ 		// Execute the module function
    /******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
    /******/ 	
    /******/ 		// Return the exports of the module
    /******/ 		return module.exports;
    /******/ 	}
    /******/ 	
    /************************************************************************/
    /******/ 	/* webpack/runtime/define property getters */
    /******/ 	(() => {
    /******/ 		// define getter functions for harmony exports
    /******/ 		__webpack_require__.d = (exports, definition) => {
    /******/ 			for(var key in definition) {
    /******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
    /******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
    /******/ 				}
    /******/ 			}
    /******/ 		};
    /******/ 	})();
    /******/ 	
    /******/ 	/* webpack/runtime/hasOwnProperty shorthand */
    /******/ 	(() => {
    /******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
    /******/ 	})();
    /******/ 	
    /******/ 	/* webpack/runtime/make namespace object */
    /******/ 	(() => {
    /******/ 		// define __esModule on exports
    /******/ 		__webpack_require__.r = (exports) => {
    /******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
    /******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
    /******/ 			}
    /******/ 			Object.defineProperty(exports, '__esModule', { value: true });
    /******/ 		};
    /******/ 	})();
    /******/ 	
    /************************************************************************/
    /******/ 	
    /******/ 	// startup
    /******/ 	// Load entry module and return exports
    /******/ 	// This entry module is referenced by other modules so it can't be inlined
    /******/ 	var __webpack_exports__ = __webpack_require__(909);
    /******/ 	
    /******/ })()
    ;