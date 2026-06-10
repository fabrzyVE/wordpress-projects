<?php
/**
 * Fallback registration for the "Calculator Pages" custom post type.
 *
 * PREFERRED: import cpt/calculator-pages-cptui.json via
 *   WP Admin > CPT UI > Tools > Import/Export > Post Types.
 *
 * Use this file only if you'd rather register the CPT in code
 * (drop it in a small site-specific plugin or a Code Snippets entry —
 * do NOT paste into a theme that may be overwritten on update).
 *
 * It is guarded so it will NOT double-register if CPT UI already
 * registered the `calculator` post type.
 */

add_action( 'init', function () {
	if ( post_type_exists( 'calculator' ) ) {
		return; // CPT UI (or another source) already registered it.
	}

	$labels = array(
		'name'               => 'Calculator Pages',
		'singular_name'      => 'Calculator Page',
		'menu_name'          => 'Calculator Pages',
		'all_items'          => 'All Calculator Pages',
		'add_new'            => 'Add New',
		'add_new_item'       => 'Add New Calculator Page',
		'edit_item'          => 'Edit Calculator Page',
		'new_item'           => 'New Calculator Page',
		'view_item'          => 'View Calculator Page',
		'search_items'       => 'Search Calculator Pages',
		'not_found'          => 'No calculator pages found',
		'not_found_in_trash' => 'No calculator pages found in trash',
	);

	register_post_type( 'calculator', array(
		'labels'             => $labels,
		'public'             => true,
		'publicly_queryable' => true,
		'show_ui'            => true,
		'show_in_menu'       => true,
		'show_in_rest'       => true,            // Gutenberg + Elementor + LPagery REST
		'rest_base'          => 'calculator',
		'menu_position'      => 25,
		'menu_icon'          => 'dashicons-calculator',
		'has_archive'        => 'calculators',
		'rewrite'            => array( 'slug' => 'calculators', 'with_front' => true ),
		'capability_type'    => 'post',
		'hierarchical'       => false,
		'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt', 'custom-fields', 'page-attributes' ),
	) );
} );
