use super::maoris_node::MaorisNode;
use image::GrayImage;
use petgraph::graph::UnGraph;
use std::collections::{HashMap, HashSet};

/// Performs the watershed algorithm on the given image.
///
/// The watershed algorithm is used to segment an image into distinct regions.
/// This function processes each pixel in the image and identifies regions based on pixel intensity.
///
/// # Arguments
///
/// * `image` - A reference to a `GrayImage`, representing the image to be processed.
///
/// # Returns
///
/// A vector of `Node` structures, where each `Node` represents a region in the image.
pub fn watershed(image: &GrayImage) -> Vec<MaorisNode> {
    let mut regions = Vec::new();
    let (width, height) = image.dimensions();
    let mut image_copy = image.clone();
    for y in 0..height {
        for x in 0..width {
            // Skip pixels that have already been processed (set to 0)
            if image_copy.get_pixel(x, y)[0] == 0 {
                continue;
            }

            // Process the region starting from the current pixel
            let pixels = watershed_from_one_pixel(&mut image_copy, &image, (x, y));
            regions.push(pixels);
        }
    }
    regions
}

/// Processes the neighbors of a given pixel in an image.
///
/// This function is part of an image processing algorithm, likely related to the Watershed algorithm.
/// It updates the image and a node structure based on the pixel values.
///
/// # Arguments
///
/// * `image` - A mutable reference to a `GrayImage`, representing the image being processed.
/// * `pixels` - A mutable reference to a `Node`, representing a data structure for managing pixels and their neighbors.
/// * `current_pixel` - A tuple `(u32, u32)` representing the coordinates of the current pixel being processed.
/// * `pixel_value` - A `u8` value representing the intensity value of the current pixel.
fn process_neighbors(
    image: &mut GrayImage,
    original_image: &GrayImage,
    pixels: &mut MaorisNode,
    current_pixel: (u32, u32),
    pixel_value: u8,
) -> () {
    let directions = [
        (1, 0),   // right
        (-1, 0),  // left
        (0, -1),  // up
        (0, 1),   // down
        (1, -1),  // up-right
        (1, 1),   // down-right
        (-1, 1),  // down-left
        (-1, -1), // up-left
    ];

    for &(dx, dy) in &directions {
        let neighbor_x = current_pixel.0 as isize + dx;
        let neighbor_y = current_pixel.1 as isize + dy;

        if neighbor_x >= 0
            && neighbor_x < image.width() as isize
            && neighbor_y >= 0
            && neighbor_y < image.height() as isize
        {
            let neighbor_pixel = (neighbor_x as u32, neighbor_y as u32);
            let neighbor_value = image.get_pixel(neighbor_pixel.0, neighbor_pixel.1)[0];
            let original_neighbor_value =
                original_image.get_pixel(neighbor_pixel.0, neighbor_pixel.1)[0];
            if neighbor_value == pixel_value {
                pixels.add_pixel(neighbor_pixel);
                image.get_pixel_mut(neighbor_pixel.0, neighbor_pixel.1)[0] = 0;
            } else if neighbor_value != 0 {
                pixels.add_neighbor_pixel(neighbor_pixel);
            }

            if original_neighbor_value != pixel_value {
                //Current pixel is part of the regions contour
                pixels.add_contour_pixel(current_pixel);
            }
        }
    }
}

fn watershed_from_one_pixel(
    image: &mut GrayImage,
    original_image: &GrayImage,
    start_pixel: (u32, u32),
) -> MaorisNode {
    let pixel_value = image.get_pixel(start_pixel.0, start_pixel.1)[0];
    let mut pixels = MaorisNode::from_value(pixel_value);
    pixels.add_pixel(start_pixel);
    image.get_pixel_mut(start_pixel.0, start_pixel.1)[0] = 0;

    let mut index = 0;
    while index < pixels.pixels.len() {
        let current_pixel = pixels.pixels[index];
        index += 1;
        // Usage in the main function or wherever appropriate
        process_neighbors(
            image,
            original_image,
            &mut pixels,
            current_pixel,
            pixel_value,
        );
    }
    return pixels;
}

pub fn image_to_graph(image: &GrayImage) -> UnGraph<MaorisNode, ()> {
    let mut graph = UnGraph::new_undirected();

    let regions = watershed(&image);
    for region in regions {
        graph.add_node(region);
    }

    let mut pixel_to_nodes = HashMap::new();
    // Precompute a map from pixels to nodes
    for node in graph.node_indices() {
        for pixel in &graph[node].pixels {
            pixel_to_nodes
                .entry(*pixel)
                .or_insert_with(Vec::new)
                .push(node);
        }
    }
    let mut edges_to_add = HashSet::new();

    //Add edges by on neighbor pixels
    for node in graph.node_indices() {
        for neighbor_pixel in &graph[node].neighbor_pixels {
            if let Some(neighbor_nodes) = pixel_to_nodes.get(neighbor_pixel) {
                for neighbor_node in neighbor_nodes {
                    edges_to_add.insert((node, *neighbor_node));
                }
            }
        }
    }

    for (node, neighbor_node) in edges_to_add {
        graph.add_edge(node, neighbor_node, ());
    }

    graph
}

// Unit tests
#[cfg(test)]
mod test {
    use image::Luma;

    use super::*;

    #[test]
    fn test_watershed() -> () {
        // a default (black) image
        let mut test_image: GrayImage = GrayImage::new(3, 3);
        // Set each pixel to 1
        for pixel in test_image.pixels_mut() {
            *pixel = Luma([1]);
        }

        test_image.get_pixel_mut(0, 0).0 = [255];
        test_image.get_pixel_mut(2, 2).0 = [255];

        let regions = watershed(&test_image);

        assert_eq!(regions.len(), 3);
        assert_eq!(regions[0].pixels.len(), 1);
        assert_eq!(regions[1].pixels.len(), 7);
        assert_eq!(regions[2].pixels.len(), 1);

        // Test that the nieghbor pixel are correct
        assert_eq!(regions[0].neighbor_pixels.len(), 3);
        // Neighbor are only saved in one direction so at each step there are less tha planned
        assert_eq!(regions[1].neighbor_pixels.len(), 1);
        assert_eq!(regions[2].neighbor_pixels.len(), 0);

        assert_eq!(regions[0].contour_pixels.len(), 1);
        assert_eq!(regions[1].contour_pixels.len(), 5);
        assert_eq!(regions[2].contour_pixels.len(), 1);
    }

    #[test]
    fn test_to_graph() -> () {
        // a default (black) image
        let mut test_image: GrayImage = GrayImage::new(3, 3);
        // Set each pixel to 1
        for pixel in test_image.pixels_mut() {
            *pixel = Luma([1]);
        }

        test_image.get_pixel_mut(0, 0).0 = [255];
        test_image.get_pixel_mut(2, 2).0 = [255];
        test_image.get_pixel_mut(0, 2).0 = [255];
        test_image.get_pixel_mut(2, 0).0 = [255];

        let graph = image_to_graph(&test_image);
        assert_eq!(graph.node_count(), 5);
        assert_eq!(graph.edge_count(), 4);
    }
}
