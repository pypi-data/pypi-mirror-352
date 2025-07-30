# validation_utils.py
import frappe
from frappe import _

def validate_integration_setup(doc, integration_type):
    """
    Validate that required settings are configured for the selected integration type
    """
    errors = []
    
    if integration_type == 'pos_invoice':
        errors.extend(validate_pos_invoice_setup(doc))
    elif integration_type == 'sales_invoice':
        errors.extend(validate_sales_invoice_setup(doc))
    elif integration_type == 'sales_order':
        errors.extend(validate_sales_order_setup(doc))
    
    if errors:
        frappe.throw(_("Integration setup validation failed:\n") + "\n".join(errors))

def validate_pos_invoice_setup(doc):
    """Validate POS Invoice integration requirements"""
    errors = []
    
    # Check if POS Profile exists
    if not doc.pos_profile:
        errors.append("• POS Profile is required for POS Invoice integration")
    
    # Validate POS Profile configuration
    if doc.pos_profile:
        pos_profile = frappe.get_doc("POS Profile", doc.pos_profile)
        if not pos_profile.warehouse:
            errors.append("• POS Profile must have a default warehouse configured")
        if not pos_profile.income_account:
            errors.append("• POS Profile must have an income account configured")
        if not pos_profile.cost_center:
            errors.append("• POS Profile must have a cost center configured")
    
    return errors

def validate_sales_invoice_setup(doc):
    """Validate Sales Invoice integration requirements"""
    errors = []
    
    # Check required accounts
    if not doc.tax_account:
        errors.append("• Tax Account is required for Sales Invoice integration")
    
    # Check price list
    if not doc.price_list:
        errors.append("• Price List is required for Sales Invoice integration")
    
    return errors

def validate_sales_order_setup(doc):
    """Validate Sales Order integration requirements"""
    errors = []
    
    # Check warehouse
    if not doc.custom_warehouse:
        errors.append("• Default Warehouse is required for Sales Order integration")
    
    # Check delivery days
    if not doc.custom_days_to_delivery_order or doc.custom_days_to_delivery_order < 1:
        errors.append("• Days to Delivery must be at least 1 for Sales Order integration")
    
    # Check price list
    if not doc.price_list:
        errors.append("• Price List is required for Sales Order integration")
    
    return errors

def validate_payment_method_mapping():
    """Validate that payment methods are properly mapped"""
    # Check if there are any Salla orders with unmapped payment methods
    unmapped_methods = frappe.db.sql("""
        SELECT DISTINCT salla_payment_method 
        FROM `tabSalla Order` 
        WHERE salla_payment_method NOT IN (
            SELECT salla_payment_method 
            FROM `tabSalla Payment Method Mapping`
        )
        AND docstatus = 1
    """, as_dict=True)
    
    if unmapped_methods:
        methods = [method.salla_payment_method for method in unmapped_methods]
        frappe.msgprint(
            _("Warning: The following payment methods are not mapped: {0}").format(", ".join(methods)),
            alert=True
        )

def validate_shipment_method_mapping():
    """Validate that shipment methods are properly mapped"""
    # Check if there are any Salla orders with unmapped shipment methods
    unmapped_methods = frappe.db.sql("""
        SELECT DISTINCT salla_shipping_method 
        FROM `tabSalla Order` 
        WHERE salla_shipping_method NOT IN (
            SELECT salla_shipment_method 
            FROM `tabSalla Shipment Method Mapping`
        )
        AND docstatus = 1
        AND salla_shipping_method IS NOT NULL
        AND salla_shipping_method != ''
    """, as_dict=True)
    
    if unmapped_methods:
        methods = [method.salla_shipping_method for method in unmapped_methods]
        frappe.msgprint(
            _("Warning: The following shipment methods are not mapped: {0}").format(", ".join(methods)),
            alert=True
        )

def check_integration_health():
    """
    Check the health of the integration and return status report
    """
    health_report = {
        'status': 'healthy',
        'warnings': [],
        'errors': [],
        'statistics': {}
    }
    
    try:
        # Get integration type
        salla_defaults = frappe.get_single("Salla Defaults")
        integration_type = salla_defaults.integration_type
        
        # Check for failed integrations
        failed_orders = frappe.db.count("Salla Order", {
            "docstatus": 1,
            f"custom_{integration_type.replace('_', '_')}_name": ["is", "not set"]
        })
        
        if failed_orders > 0:
            health_report['warnings'].append(f"{failed_orders} orders failed to create {integration_type.replace('_', ' ').title()}")
        
        # Check mapping completeness
        validate_payment_method_mapping()
        validate_shipment_method_mapping()
        
        # Get statistics
        health_report['statistics'] = {
            'total_orders': frappe.db.count("Salla Order", {"docstatus": 1}),
            'successful_integrations': frappe.db.count("Salla Order", {
                "docstatus": 1,
                f"custom_{integration_type.replace('_', '_')}_name": ["is", "set"]
            }),
            'integration_type': integration_type
        }
        
        # Calculate success rate
        total = health_report['statistics']['total_orders']
        successful = health_report['statistics']['successful_integrations']
        
        if total > 0:
            success_rate = (successful / total) * 100
            health_report['statistics']['success_rate'] = f"{success_rate:.1f}%"
            
            if success_rate < 95:
                health_report['status'] = 'warning'
            if success_rate < 80:
                health_report['status'] = 'critical'
        
    except Exception as e:
        health_report['status'] = 'error'
        health_report['errors'].append(f"Health check failed: {str(e)}")
    
    return health_report

@frappe.whitelist()
def get_integration_health():
    """API endpoint to get integration health status"""
    return check_integration_health()

@frappe.whitelist()
def validate_current_setup():
    """API endpoint to validate current integration setup"""
    try:
        salla_defaults = frappe.get_single("Salla Defaults")
        validate_integration_setup(salla_defaults, salla_defaults.integration_type)
        return {"status": "success", "message": "Integration setup is valid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}