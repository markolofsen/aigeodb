/**
 * AigeoDB Django autocomplete initialization
 * Automatically initializes CityField and CountryField autocomplete widgets
 * with dark theme by default.
 */
(function($) {
    'use strict';

    // Only run in Django admin
    if (typeof django === 'undefined' || !django.jQuery) {
        console.log('AigeoDB: Not in Django admin, skipping autocomplete init');
        return;
    }

    // Initialize Select2 widgets
    function initSelect2Widgets() {
        $('.admin-autocomplete').each(function() {
            // Skip if already initialized
            if ($(this).hasClass('select2-hidden-accessible')) {
                return;
            }

            var $select = $(this);
            var widgetId = $select.attr('id');
            var initialData = window.WIDGET_INITIAL_DATA && window.WIDGET_INITIAL_DATA[widgetId];

            // Force dark theme configuration
            var config = {
                theme: 'admin-dark',  // Force dark theme
                placeholder: $select.data('placeholder'),
                allowClear: true,
                minimumInputLength: parseInt($select.data('minimum-input-length') || '2'),
                width: $select.data('width') || '100%',
                dropdownParent: $select.closest('form'),
                containerCssClass: 'select2-dark-container',
                dropdownCssClass: 'select2-dark-dropdown',
                ajax: {
                    url: $select.data('ajax-url'),
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            term: params.term,
                            page: params.page || 1
                        };
                    },
                    processResults: function(data) {
                        return {
                            results: data.results || [],
                            pagination: {
                                more: data.pagination?.more || false
                            }
                        };
                    },
                    cache: true
                }
            };

            // Initialize Select2
            $select.select2(config);

            // Set initial value if exists
            if (initialData) {
                console.log('Setting initial value for', widgetId, initialData);
                var option = new Option(
                    initialData.text,
                    initialData.id,
                    true,
                    true
                );
                $select.append(option);
                $select.trigger('change');
                // Force update the display
                $select.select2('data', [{
                    id: initialData.id,
                    text: initialData.text
                }]);
            }

            // Focus search field when opened
            $select.on('select2:open', function() {
                setTimeout(function() {
                    $('.select2-search__field').focus();
                }, 0);
            });

            // Force dark theme on dropdown
            $select.on('select2:open', function() {
                $('.select2-dropdown').addClass('select2-dark-dropdown');
                $('.select2-search__field').addClass('select2-dark-search');
            });
        });
    }

    // Initialize when DOM is ready
    $(document).ready(function() {
        initSelect2Widgets();
        
        // Also initialize when admin inline forms are added
        $(document).on('formset:added', function() {
            setTimeout(initSelect2Widgets, 10);
        });
    });

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize all admin-autocomplete fields
        document.querySelectorAll('.admin-autocomplete').forEach(function(element) {
            let config = {
                theme: element.dataset.theme || 'admin',
                placeholder: element.dataset.placeholder,
                minimumInputLength: parseInt(element.dataset.minimumInputLength || '2'),
                ajax: {
                    url: element.dataset.ajaxUrl,
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            term: params.term,
                            page: params.page || 1
                        };
                    },
                    processResults: function(data) {
                        return {
                            results: data.results,
                            pagination: {
                                more: data.pagination?.more
                            }
                        };
                    }
                }
            };

            // Initialize Select2
            $(element).select2(config);

            // Set initial value if exists
            let widgetId = element.id;
            if (window.WIDGET_INITIAL_DATA && window.WIDGET_INITIAL_DATA[widgetId]) {
                let option = new Option(
                    window.WIDGET_INITIAL_DATA[widgetId].text,
                    window.WIDGET_INITIAL_DATA[widgetId].id,
                    true,
                    true
                );
                $(element).append(option).trigger('change');
            }
        });
    });

})(django.jQuery); 