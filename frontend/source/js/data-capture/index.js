
// entrypoint for data-capture
// this is where modules should be `require(...)`'d


const installCE = require('document-register-element/pony');

// Because the CustomElements spec is interpreted differently
// by different browsers, we're just going to force-apply
// document-register-element's interpretation of the spec
// so we have a consistent experience across all browsers.
installCE(global, 'force');

require('./upload');
require('./ajaxform');
require('./alerts');
require('./expandable-area');
require('./date');
require('./smooth-scroll');
require('./modal-dialogs');
require('./edit-details-form-enhance');
require('./form-validation');
