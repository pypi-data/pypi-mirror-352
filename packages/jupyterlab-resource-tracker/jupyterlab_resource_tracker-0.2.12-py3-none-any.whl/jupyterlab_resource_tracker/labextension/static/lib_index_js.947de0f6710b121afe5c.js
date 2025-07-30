"use strict";
(self["webpackChunkjupyterlab_resource_tracker"] = self["webpackChunkjupyterlab_resource_tracker"] || []).push([["lib_index_js"],{

/***/ "./lib/components/DashboardComponent.js":
/*!**********************************************!*\
  !*** ./lib/components/DashboardComponent.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/Refresh */ "./node_modules/@mui/icons-material/esm/Refresh.js");
/* harmony import */ var _SummaryComponent__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./SummaryComponent */ "./lib/components/SummaryComponent.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);




// import DetailsComponent from './DetailsComponent';


const DashboardComponent = () => {
    const [summaryList, setSummaryList] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    // const [detailList, setDetailList] = React.useState<Detail[]>([]);
    const [loading, setLoading] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        getLogs();
    }, []);
    const getLogs = async () => {
        var _a, _b;
        setLoading(true);
        try {
            const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('usages-costs/logs', {
                method: 'GET',
            });
            if (response) {
                setSummaryList(response.summary);
                // setDetailList(response.details);
            }
        }
        catch (error) {
            console.error('Error fetching logs:', error);
            let errorMessage = 'An unexpected error occurred.';
            if (error && error.response && error.response.status) {
                switch (error.response.status) {
                    case 400:
                        errorMessage = 'Invalid log file format. Please check the logs.';
                        break;
                    case 404:
                        errorMessage = 'Log files not found. Ensure they exist in the configured path.';
                        break;
                    case 500:
                        console.error('Error response from server:', error.response);
                        errorMessage =
                            'Server error: ' +
                                (((_a = error.response.data) === null || _a === void 0 ? void 0 : _a.error) || 'Unknown issue');
                        break;
                    default:
                        errorMessage = ((_b = error.response.data) === null || _b === void 0 ? void 0 : _b.error) || 'Unexpected error.';
                }
            }
            else if (error === null || error === void 0 ? void 0 : error.message) {
                errorMessage = error.message;
            }
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showErrorMessage)('Error Fetching Logs', errorMessage);
        }
        finally {
            setLoading(false);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.AppBar, { position: "static", color: "primary" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Toolbar, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", sx: { flexGrow: 1 } }, "Dashboard"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Tooltip, { title: "Refresh Data" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { color: "inherit", onClick: getLogs, disabled: loading }, loading ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CircularProgress, { size: 24, color: "inherit" }) : react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_4__["default"], null))))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { p: 2, height: '92%', overflowY: 'auto' } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_SummaryComponent__WEBPACK_IMPORTED_MODULE_5__["default"], { summary: summaryList, loading: loading }))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DashboardComponent);


/***/ }),

/***/ "./lib/components/SummaryComponent.js":
/*!********************************************!*\
  !*** ./lib/components/SummaryComponent.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/x-data-grid */ "webpack/sharing/consume/default/@mui/x-data-grid/@mui/x-data-grid");
/* harmony import */ var _mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__);



const SummaryComponent = (props) => {
    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'project', headerName: 'Project', width: 130 },
        { field: 'podName', headerName: 'Pod name', width: 150 },
        { field: 'usage', headerName: 'Usage (time)', type: 'number', width: 130 },
        {
            field: 'cost',
            headerName: 'ToDate Cost ($)',
            type: 'number',
            width: 130
        },
        { field: 'month', headerName: 'Month', width: 100 },
        { field: 'year', headerName: 'Year', width: 100 },
        { field: 'lastUpdate', headerName: 'Updated', width: 200 }
    ];
    const paginationModel = { page: 0, pageSize: 10 };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", gutterBottom: true }, "Monthly costs and usages to date"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Paper, { sx: { p: 2, boxShadow: 3, borderRadius: 2, mb: 2 } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_x_data_grid__WEBPACK_IMPORTED_MODULE_2__.DataGrid, { autoHeight: true, rows: props.summary, columns: columns, loading: props.loading, initialState: {
                    pagination: { paginationModel },
                    columns: {
                        columnVisibilityModel: {
                            id: false
                        }
                    }
                }, pageSizeOptions: [10, 20, 30], disableRowSelectionOnClick: true, sx: { border: 0 } }))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SummaryComponent);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-resource-tracker', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _widgets_DashboardWidget__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./widgets/DashboardWidget */ "./lib/widgets/DashboardWidget.js");






const PLUGIN_ID = 'jupyterlab-resource-tracker:plugin';
const PALETTE_CATEGORY = 'Admin tools';
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.createNew = 'jupyterlab-resource-tracker:open-dashboard';
})(CommandIDs || (CommandIDs = {}));
/**
 * Initialization data for the jupyterlab-resource-tracker extension.
 */
const plugin = {
    id: PLUGIN_ID,
    description: 'A JupyterLab extension.',
    autoStart: true,
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__.ISettingRegistry, _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_1__.ILauncher, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette],
    activate: (app, settingRegistry, launcher, palette) => {
        console.log('JupyterLab extension jupyterlab-resource-tracker is activated!');
        if (settingRegistry) {
            settingRegistry
                .load(plugin.id)
                .then(settings => {
                console.log('jupyterlab-resource-tracker settings loaded:', settings.composite);
            })
                .catch(reason => {
                console.error('Failed to load settings for jupyterlab-resource-tracker.', reason);
            });
        }
        (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('get-example')
            .then(data => {
            console.log(data);
        })
            .catch(reason => {
            console.error(`The jupyterlab_resource_tracker server extension appears to be missing.\n${reason}`);
        });
        const { commands } = app;
        const command = CommandIDs.createNew;
        // const sideBarContent = new NBQueueSideBarWidget(s3BucketId);
        // const sideBarWidget = new MainAreaWidget<NBQueueSideBarWidget>({
        //   content: sideBarContent
        // });
        // sideBarWidget.toolbar.hide();
        // sideBarWidget.title.icon = runIcon;
        // sideBarWidget.title.caption = 'NBQueue job list';
        // app.shell.add(sideBarWidget, 'right', { rank: 501 });
        // Define a widget creator function,
        // then call it to make a new widget
        const newWidget = () => {
            // Create a blank content widget inside of a MainAreaWidget
            const dashboardContent = new _widgets_DashboardWidget__WEBPACK_IMPORTED_MODULE_5__.DashboardWidget();
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget({
                content: dashboardContent
            });
            widget.id = 'resource-tracker-dashboard';
            widget.title.label = 'Resource Tracker';
            widget.title.closable = true;
            return widget;
        };
        let widget = newWidget();
        commands.addCommand(command, {
            label: 'Resource Tracker',
            caption: 'Resource Tracker',
            icon: args => (args['isPalette'] ? undefined : _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.inspectorIcon),
            execute: async (args) => {
                console.log('Command executed');
                // Regenerate the widget if disposed
                if (widget.isDisposed) {
                    widget = newWidget();
                }
                if (!widget.isAttached) {
                    // Attach the widget to the main work area if it's not there
                    app.shell.add(widget, 'main');
                }
                // Activate the widget
                app.shell.activateById(widget.id);
            }
        });
        if (launcher) {
            launcher.add({
                command,
                category: 'Admin tools',
                rank: 1
            });
        }
        if (palette) {
            palette.addItem({
                command,
                args: { isPalette: true },
                category: PALETTE_CATEGORY
            });
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/widgets/DashboardWidget.js":
/*!****************************************!*\
  !*** ./lib/widgets/DashboardWidget.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DashboardWidget: () => (/* binding */ DashboardWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_DashboardComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/DashboardComponent */ "./lib/components/DashboardComponent.js");



class DashboardWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    constructor() {
        super();
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_DashboardComponent__WEBPACK_IMPORTED_MODULE_2__["default"], null));
    }
}


/***/ }),

/***/ "./node_modules/@mui/icons-material/esm/Refresh.js":
/*!*********************************************************!*\
  !*** ./node_modules/@mui/icons-material/esm/Refresh.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_createSvgIcon_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils/createSvgIcon.js */ "./node_modules/@mui/material/utils/createSvgIcon.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
"use client";



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ((0,_utils_createSvgIcon_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_0__.jsx)("path", {
  d: "M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z"
}), 'Refresh'));

/***/ })

}]);
//# sourceMappingURL=lib_index_js.947de0f6710b121afe5c.js.map