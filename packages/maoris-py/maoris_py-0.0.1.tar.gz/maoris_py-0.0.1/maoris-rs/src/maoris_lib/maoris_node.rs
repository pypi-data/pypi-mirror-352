use std::collections::HashSet;

/// A structure representing a node in the graph.
///
/// Each `Node` contains a list of pixels and a set of neighboring pixels.
#[derive(Clone)]
pub struct MaorisNode {
    /// A vector of pixel coordinates `(u32, u32)` that belong to this node.
    pub pixels: Vec<(u32, u32)>,
    /// A set of pixel coordinates `(u32, u32)` that are neighbors to the pixels in this node.
    pub neighbor_pixels: HashSet<(u32, u32)>,
    pub contour_pixels: HashSet<(u32, u32)>,
    pub value: u8,
}

impl MaorisNode {
    /// Adds a pixel to the node.
    ///
    /// This method appends the given pixel position to the list of pixels in the node.
    ///
    /// # Arguments
    ///
    /// * `position` - A tuple `(u32, u32)` representing the coordinates of the pixel to be added.
    pub fn add_pixel(&mut self, position: (u32, u32)) {
        self.pixels.push(position);
    }

    /// Adds a neighbor pixel to the node.
    ///
    /// This method inserts the given neighbor pixel position into the set of neighbor pixels in the node.
    ///
    /// # Arguments
    ///
    /// * `position` - A tuple `(u32, u32)` representing the coordinates of the neighbor pixel to be added.
    pub fn add_neighbor_pixel(&mut self, position: (u32, u32)) {
        self.neighbor_pixels.insert(position);
    }

    pub fn add_contour_pixel(&mut self, position: (u32, u32)) {
        self.contour_pixels.insert(position);
    }

    /// Creates a new `Node` with empty pixel and neighbor pixel collections.
    ///
    /// # Returns
    ///
    /// A new `Node` instance with empty vectors and sets for pixels and neighbor pixels, respectively.
    pub fn from_value(value_node: u8) -> Self {
        MaorisNode {
            pixels: Vec::new(),
            neighbor_pixels: HashSet::new(),
            contour_pixels: HashSet::new(),
            value: value_node,
        }
    }

    pub fn in_contact(point1: (u32, u32), point2: (u32, u32)) -> bool {
        let (x1, y1) = point1;
        let (x2, y2) = point2;
        let dx = (x1 as i32 - x2 as i32).abs();
        let dy = (y1 as i32 - y2 as i32).abs();
        dx <= 1 && dy <= 1
    }
}

// Unit tests
#[cfg(test)]
mod test {

    use super::*;

    #[test]
    fn test_in_contact() -> () {
        let point1 = (0, 0);
        let point2 = (0, 1);
        let point3 = (1, 3);
        assert!(MaorisNode::in_contact(point1, point2));
        assert!(!MaorisNode::in_contact(point1, point3));
    }
}
