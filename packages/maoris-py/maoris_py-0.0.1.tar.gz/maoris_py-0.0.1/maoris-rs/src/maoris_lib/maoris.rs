use std::{
    collections::{HashMap, HashSet, VecDeque},
    usize,
};

use image::Luma;
use parking_lot::Mutex;
use petgraph::{
    graph::{NodeIndex, UnGraph},
    EdgeType, Graph,
};

use super::maoris_node::MaorisNode;

#[derive(Clone)]
pub struct MaorisNodeHash {
    pub pixels: HashSet<(u32, u32)>,
    pub contour_pixels: HashSet<(u32, u32)>,
    pub value: u8,
}

impl MaorisNodeHash {
    pub fn from(maoris_node: &MaorisNode) -> Self {
        Self {
            pixels: maoris_node.pixels.clone().into_iter().collect(),
            contour_pixels: maoris_node.contour_pixels.clone(),
            value: maoris_node.value,
        }
    }

    pub fn merge(&mut self, node: &MaorisNodeHash) -> () {
        self.pixels.extend(&node.pixels);
        self.contour_pixels.extend(&node.contour_pixels);
        self.set_countour_pixels();
    }

    /// Determines if a given pixel is a contour pixel.
    ///
    /// A pixel is considered a contour pixel if it has at least one neighbor that is not part of the node.
    /// This method checks the 8 possible neighboring positions around the given pixel.
    ///
    /// # Arguments
    ///
    /// * `pixel` - A tuple `(u32, u32)` representing the coordinates of the pixel to be checked.
    ///
    /// # Returns
    ///
    /// `true` if the pixel is a contour pixel, `false` otherwise.
    fn is_contour_pixel(&self, pixel: (u32, u32)) -> bool {
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

        let mut count = 0;
        for &(dx, dy) in &directions {
            let neighbor_x = pixel.0 as isize + dx;
            let neighbor_y = pixel.1 as isize + dy;

            if neighbor_x < 0 || neighbor_y < 0 {
                return true;
            }

            if self
                .pixels
                .contains(&(neighbor_x as u32, neighbor_y as u32))
            {
                count += 1;
            }
        }
        if count == 8 {
            return false;
        }
        return true;
    }

    fn set_countour_pixels(&mut self) {
        let contour_pixels_tmp = Mutex::new(HashSet::new());

        self.contour_pixels.iter().for_each(|pixel| {
            if self.is_contour_pixel(*pixel) {
                contour_pixels_tmp.lock().insert(*pixel);
            }
        });

        self.contour_pixels = contour_pixels_tmp.into_inner();
    }

    pub fn is_ripple_of(&self, node: &MaorisNodeHash) -> bool {
        let mut in_contact = 0;
        for pixel1 in self.contour_pixels.iter() {
            for pixel2 in node.contour_pixels.iter() {
                if MaorisNode::in_contact(*pixel1, *pixel2) {
                    in_contact += 1;
                    break;
                }
            }
        }
        if in_contact * 100 / self.contour_pixels.len() >= 40 {
            return true;
        }
        return false;
    }

    ///A function that draw the pixel in final_node on a image based on the value in final_node
    pub fn draw_set_value(&self, image: &mut image::GrayImage, value: u8) {
        for pixel in &self.pixels {
            if value == 0 {
                image.put_pixel(pixel.0, pixel.1, Luma([self.value]));
            } else {
                image.put_pixel(pixel.0, pixel.1, Luma([value]));
            }
        }
    }

    pub fn draw(&self, image: &mut image::GrayImage) {
        self.draw_set_value(image, 0);
    }

    pub fn is_similar(&self, node: &MaorisNodeHash, edge_value: u8, t_merging: f64) -> bool {
        //TODO: see if the value of the original zone is used in the c++ implementation or
        // the value from the original zones in contact
        if node.value > self.value {
            //Return false because this should have already been visited
            return false;
        }

        //Similar value
        let val = f64::from(self.value);
        let node_val = f64::from(node.value);
        let edge_val = f64::from(edge_value);

        if (val - node_val).abs() <= val * t_merging {
            //Not a door with self
            if (val - edge_val).abs() <= val * t_merging {
                //Not a door with node
                if (node_val - edge_val).abs() <= node_val * t_merging {
                    return true;
                }
            }
        }
        return false;
    }
}

/// A struct representing a super node in the Maoris graph.
///
/// This struct contains a list of nodes that are part of this super node and
/// a final node that represents the merged state of all nodes in this super node.
pub struct SuperMaorisNode {
    /// A vector of node indices that are part of this super node.
    nodes: HashSet<NodeIndex>,
    /// The final merged node that represents the state of this super node.
    pub final_node: MaorisNodeHash,
    largest_node_size: usize,
    neighbors: HashMap<NodeIndex, u8>,
}

impl SuperMaorisNode {
    pub fn from<E, Tdir>(maoris_node: &NodeIndex, graph: &Graph<MaorisNodeHash, E, Tdir>) -> Self
    where
        Tdir: EdgeType,
    {
        let mut neighbors: HashMap<NodeIndex, u8> = HashMap::new();
        neighbors.insert(*maoris_node, graph[*maoris_node].value);

        let mut super_node = Self {
            nodes: vec![*maoris_node].into_iter().collect(),
            final_node: graph[*maoris_node].clone(),
            neighbors,
            largest_node_size: graph[*maoris_node].pixels.len(),
        };
        super_node.add_neighbors(maoris_node, graph);
        super_node
    }

    fn add_neighbors<E, Tdir>(&mut self, node: &NodeIndex, graph: &Graph<MaorisNodeHash, E, Tdir>)
    where
        Tdir: EdgeType,
    {
        //Get the value associated to the node in the list of neighbors
        let node_value = self.neighbors[node];
        for neighbor in graph.neighbors(*node) {
            //Skip if the node is already part of the super node
            if self.nodes.contains(&neighbor) {
                continue;
            }

            //Otherwise add to the list of neighbors for exploration and
            // keep as the value the shortest value explored in this path
            // Which is either the value of the neighbor or the value previously associated with the node added to the super node.
            let smallest_value = std::cmp::min(node_value, graph[neighbor].value);

            self.neighbors.insert(neighbor, smallest_value);
        }
        self.neighbors.remove(node);
    }

    pub fn add<E, Tdir>(&mut self, node: &NodeIndex, graph: &Graph<MaorisNodeHash, E, Tdir>)
    where
        Tdir: EdgeType,
    {
        self.nodes.insert(*node);
        self.final_node.merge(&graph[*node]);
        if self.largest_node_size < graph[*node].pixels.len() {
            self.largest_node_size = graph[*node].pixels.len();
            self.final_node.value = graph[*node].value;
        }
        self.add_neighbors(node, graph);
    }

    pub fn contains(&self, node: &NodeIndex) -> bool {
        self.nodes.contains(&node)
    }

    pub fn get_distance(&self, node: &NodeIndex, graph: &UnGraph<MaorisNodeHash, ()>) -> f32 {
        let mut min_edge_value = f32::MAX;
        let neighbors = graph.neighbors(*node);
        for neighbor in neighbors {
            if self.nodes.contains(&neighbor) {
                let val = f32::from(graph[*node].value);
                let n_val = f32::from(graph[neighbor].value);
                let distance = (val - n_val).abs();
                if distance < min_edge_value {
                    min_edge_value = distance;
                }
            }
        }
        if min_edge_value == f32::MAX {
            panic!("No neighbor found");
        }
        min_edge_value
    }

    /// Get the neighbors of the super node in the super graph
    /// and their smallest edge value to the super node
    pub fn get_super_node_neighbors(
        &self,
        mapping: &HashMap<NodeIndex, usize>,
    ) -> HashMap<usize, u8> {
        let mut super_neighbors: HashMap<usize, u8> = HashMap::new();
        for neighbor in &self.neighbors {
            let super_neighbor = mapping[neighbor.0];
            if super_neighbors.contains_key(&super_neighbor) {
                let current_min = super_neighbors[&super_neighbor];
                if *neighbor.1 < current_min {
                    if let Some(val) = super_neighbors.get_mut(&super_neighbor) {
                        *val = *neighbor.1;
                    }
                }
            } else {
                super_neighbors.insert(mapping[neighbor.0], *neighbor.1);
            }
        }
        super_neighbors
    }
}

pub struct Maoris {
    pub graph: UnGraph<MaorisNodeHash, ()>,
    pub index_to_super_pixel: HashMap<NodeIndex, usize>, // node index to super pixel index
    pub final_nodes: Vec<SuperMaorisNode>,               // super pixel index to super pixel
}

impl Maoris {
    /// Converts the nodes in the graph to a vector of tuples for sorting.
    ///
    /// Each tuple contains the value of the node, the number of pixels in the node,
    /// and the node index. The nodes are sorted by their value in descending order.
    /// If two nodes have the same value, they are sorted by the number of pixels in ascending order.
    ///
    /// # Returns
    ///
    /// A vector of tuples `(u8, usize, NodeIndex)` representing the nodes in the graph.
    fn nodes_as_vec<E, Tdir>(graph: &Graph<MaorisNodeHash, E, Tdir>) -> Vec<(u8, usize, NodeIndex)>
    where
        Tdir: EdgeType,
    {
        // List node and value for sorting
        let mut nodes: Vec<(u8, usize, NodeIndex)> = Vec::new();

        for node in graph.node_indices() {
            nodes.push((graph[node].value, graph[node].pixels.len(), node));
        }
        // Sort by value. If equal, sort by number of pixels
        nodes.sort_by(|a, b| a.0.cmp(&b.0).then_with(|| a.1.cmp(&b.1)));
        return nodes;
    }

    fn transform_graph(graph: &UnGraph<MaorisNode, ()>) -> UnGraph<MaorisNodeHash, ()> {
        let mut node_map = HashMap::new();
        let mut new_graph = UnGraph::<MaorisNodeHash, ()>::new_undirected();

        // Add nodes to the new graph and create the mapping
        for node in graph.node_indices() {
            let maoris_node = &graph[node];
            let new_node = MaorisNodeHash::from(&maoris_node);
            let new_node_index = new_graph.add_node(new_node);
            node_map.insert(node, new_node_index);
        }

        // Add edges to the new graph
        for edge in graph.edge_indices() {
            let (source, target) = graph.edge_endpoints(edge).unwrap();
            let new_source = node_map[&source];
            let new_target = node_map[&target];
            new_graph.add_edge(new_source, new_target, ());
        }

        new_graph
    }

    pub fn from(graph: UnGraph<MaorisNode, ()>) -> Vec<MaorisNodeHash> {
        let mut maoris = Maoris {
            graph: Maoris::transform_graph(&graph),
            index_to_super_pixel: HashMap::new(),
            final_nodes: Vec::new(),
        };

        //TODO: remove vertex under size 10 in their closest neighbor.

        //

        let graph = maoris.merge_ripples();

        let mut final_nodes: Vec<MaorisNodeHash> = Vec::new();

        //Mapping of nodes to final_nodes
        let mut merged: HashMap<NodeIndex, usize> = HashMap::new();

        //Similar code to merge_ripple to isolate in function

        let nodes = Maoris::nodes_as_vec(&graph);

        let mut super_node_count = 0;
        //go through nodes in descending order
        for (_, _, node_index) in nodes.iter().rev() {
            let mut super_node_index = super_node_count;
            // let mut super_node = &mut graph[*node_index].clone();

            if merged.contains_key(node_index) {
                super_node_index = merged[node_index];
                // super_node = &mut final_nodes[super_node_index];
            }

            for neighbor in graph.neighbors(*node_index) {
                let edge_value = graph
                    .edge_weight(graph.find_edge(*node_index, neighbor).unwrap())
                    .unwrap();
                if graph[*node_index].is_similar(&graph[neighbor], *edge_value, 0.1) {
                    merged.insert(neighbor, super_node_index);
                }
            }

            // It wasn't merged with anything to begin with
            // so it is a new super node and we need to add it to the list
            if super_node_index == super_node_count {
                super_node_count += 1;
                merged.insert(*node_index, super_node_index);
            }
        }

        let mut merged_reversed: HashMap<usize, Vec<NodeIndex>> = HashMap::new();

        for (key, val) in merged.iter() {
            if !merged_reversed.contains_key(val) {
                merged_reversed.insert(*val, vec![*key]);
            } else {
                if let Some(vec) = merged_reversed.get_mut(val) {
                    vec.push(*key);
                }
            }
        }

        for key in 0..merged_reversed.len() {
            let nodes = &merged_reversed[&key];
            let mut super_node = graph[nodes[0]].clone();
            for node in nodes {
                super_node.merge(&graph[*node]);
            }
            final_nodes.push(super_node.clone());
        }

        return final_nodes;
    }

    /// Retrieves the region and its neighbors for a given `node`.
    ///
    /// This function checks if the node and the neighbors picked are part of the super node currently being built.
    /// Neighbors are onley return if they are not part of a super node.
    ///
    /// # Arguments
    ///
    /// * `node` - A reference to the `NodeIndex` of the node to retrieve the region for.
    ///
    /// # Returns
    ///
    /// A `Result` containing a tuple with a reference to the `MaorisNodeHash` representing the region
    /// and a `HashMap` of `NodeIndex` to `u8` representing the neighbors of the region.
    /// If the node is part of the super node currently being built, it returns an error message.
    fn get_node_region(
        &self,
        node: &NodeIndex,
    ) -> Result<(&MaorisNodeHash, HashMap<NodeIndex, u8>), &str> {
        // Check that the node is not in the super_node we are building
        if self.index_to_super_pixel.contains_key(&node) {
            let region_index = self.index_to_super_pixel[&node];
            if region_index == self.final_nodes.len() {
                return Err("Node is in the super_node we are building");
            }
        }

        let mut maoris_region = &self.graph[*node];
        let neighbors_tmp = self.graph.neighbors(*node);
        let mut neighbors: HashMap<NodeIndex, u8> = HashMap::new();
        for neighbor_n_tmp in neighbors_tmp {
            neighbors.insert(neighbor_n_tmp, self.graph[neighbor_n_tmp].value);
        }

        // Change the values if the node is part of a super node
        if self.index_to_super_pixel.contains_key(node) {
            let region_index = self.index_to_super_pixel[node];
            neighbors = self.final_nodes[region_index].neighbors.clone();
            maoris_region = &self.final_nodes[region_index].final_node;
        }

        // Make sure the neighbors are not already part of a Super Node!
        let mut final_neighbors: HashMap<NodeIndex, u8> = HashMap::new();
        for neighbor in neighbors.iter() {
            if self.index_to_super_pixel.contains_key(neighbor.0) {
                continue;
            }
            final_neighbors.insert(*neighbor.0, *neighbor.1);
        }

        return Ok((maoris_region, final_neighbors));
    }

    pub fn merge_ripples(&mut self) -> UnGraph<MaorisNodeHash, u8> {
        let nodes = Maoris::nodes_as_vec(&self.graph);

        //go through nodes in descending order
        for (_, _, node_index) in nodes.iter().rev() {
            //Check that the node wasn't already merged
            if self.index_to_super_pixel.contains_key(node_index) {
                continue;
            }

            //Start a new super node
            let mut super_node = SuperMaorisNode::from(node_index, &self.graph);
            self.index_to_super_pixel
                .insert(*node_index, self.final_nodes.len());

            let to_check_hash = super_node.neighbors.clone();
            let mut to_check: VecDeque<(NodeIndex, u8)> = to_check_hash.into_iter().collect();

            while let Some(neighbor) = to_check.pop_front() {
                //Check that the neighbor is not already part of the super node we are building
                let (region, neighbor_neighbors) = match self.get_node_region(&neighbor.0) {
                    Ok((region, neighbor_neighbors)) => (region, neighbor_neighbors),
                    Err(_) => continue, //If the node is in the current super node
                };

                if !region.is_ripple_of(&super_node.final_node) {
                    continue;
                }

                let mut neighbors_to_merge_to = *node_index;
                let mut distance_value_to_merge = super_node.get_distance(&neighbor.0, &self.graph);

                for neighbor_n in neighbor_neighbors {
                    let (region_neighbors_neighbor, _) = match self.get_node_region(&neighbor_n.0) {
                        Ok((region, neighbor_neighbors)) => (region, neighbor_neighbors),
                        Err(_) => continue, //If the node is in the current super node
                    };

                    //Check ripple on full region.
                    if region.is_ripple_of(region_neighbors_neighbor) {
                        //Check distance between "original" nodes.
                        let val = f32::from(self.graph[neighbor_n.0].value);
                        let val_n = f32::from(self.graph[neighbor.0].value);
                        let distance = (val - val_n).abs();

                        if distance < distance_value_to_merge {
                            distance_value_to_merge = distance;
                            neighbors_to_merge_to = neighbor_n.0;
                        }
                    }
                }

                if neighbors_to_merge_to == neighbor.0 {
                    for node in super_node.nodes.iter() {
                        println!("{}", node.index());
                    }
                    panic!(
                        "Node {} merged with itself while checking",
                        neighbor.0.index()
                    );
                }

                //Stop if not to be merge in this super node
                if neighbors_to_merge_to != *node_index {
                    continue;
                }

                super_node.add(&neighbor.0, &self.graph);
                self.index_to_super_pixel
                    .insert(neighbor.0, self.final_nodes.len());

                let neighbors_of_merged = self.graph.neighbors(neighbor.0);
                for node_of_merged in neighbors_of_merged {
                    if !super_node.contains(&node_of_merged) {
                        to_check.push_back((node_of_merged, self.graph[node_of_merged].value));
                    }
                }
            }

            self.final_nodes.push(super_node);
        }

        self.to_graph()
    }

    fn to_graph(&self) -> UnGraph<MaorisNodeHash, u8> {
        let mut graph: UnGraph<MaorisNodeHash, u8> = UnGraph::new_undirected();

        for super_node in self.final_nodes.iter() {
            graph.add_node(super_node.final_node.clone());
        }
        let mut i = 0;
        for super_node in self.final_nodes.iter() {
            let super_neighbor = super_node.get_super_node_neighbors(&self.index_to_super_pixel);
            for neighbor in super_neighbor {
                graph.add_edge(NodeIndex::new(i), NodeIndex::new(neighbor.0), neighbor.1);
            }
            i += 1;
        }
        return graph;
    }
}

#[cfg(test)]
mod test {

    use std::collections::HashSet;

    use super::*;

    #[test]
    fn test_neighbor() -> () {
        let node1 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 1,
        };
        let node2 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 2,
        };

        let node3 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 0,
        };

        let mut graph: UnGraph<MaorisNodeHash, ()> = UnGraph::new_undirected();
        let node_index1 = graph.add_node(node1);
        let node_index2 = graph.add_node(node2);
        let node_index3 = graph.add_node(node3);
        graph.add_edge(node_index1, node_index2, ());
        graph.add_edge(node_index2, node_index3, ());

        let mut super_node = SuperMaorisNode::from(&node_index1, &graph);

        assert_eq!(super_node.neighbors.len(), 1);
        assert!(super_node.neighbors.contains_key(&node_index2));
        assert_eq!(super_node.neighbors[&node_index2], 1);

        super_node.add(&node_index2, &graph);

        assert_eq!(super_node.neighbors.len(), 1);
        assert!(super_node.neighbors.contains_key(&node_index3));
        assert_eq!(super_node.neighbors[&node_index3], 0);
    }

    #[test]
    fn test_ripples() -> () {
        let node1 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 1,
        };
        let node2 = MaorisNodeHash {
            pixels: HashSet::from([(0, 1), (1, 0), (1, 1)]),
            contour_pixels: HashSet::from([(0, 1), (1, 0), (1, 1)]),
            value: 1,
        };
        assert!(node1.is_ripple_of(&node2));
        assert!(node2.is_ripple_of(&node1));
    }

    #[test]
    fn test_merge_and_contour() -> () {
        let mut node1 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0), (0, 1), (1, 0), (1, 1)]),
            contour_pixels: HashSet::from([(0, 0), (0, 1), (1, 0), (1, 1)]),
            value: 1,
        };
        node1.set_countour_pixels();
        assert_eq!(
            node1.contour_pixels,
            HashSet::from([(0, 0), (0, 1), (1, 0), (1, 1)])
        );

        let mut node2 = MaorisNodeHash {
            pixels: HashSet::from([
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ]),
            contour_pixels: HashSet::from([
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ]),
            value: 1,
        };
        node2.set_countour_pixels();
        assert_eq!(
            node2.contour_pixels,
            HashSet::from([
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ])
        );

        node1.merge(&node2);

        let mut hashset_test = HashSet::new();
        for pixel in node1.pixels {
            hashset_test.insert(pixel);
        }
        assert_eq!(
            hashset_test,
            HashSet::from([
                (0, 0),
                (0, 1),
                (1, 0),
                (1, 1),
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ])
        );

        assert_eq!(
            node1.contour_pixels,
            HashSet::from([
                (0, 0),
                (0, 1),
                (1, 0),
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ])
        );
    }

    #[test]
    fn test_neighbor_on_side() -> () {
        let node1 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 10,
        };
        let node2 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 5,
        };

        let node3 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 1,
        };

        let node4 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 2,
        };

        let node5 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 1,
        };

        let node6 = MaorisNodeHash {
            pixels: HashSet::from([(0, 0)]),
            contour_pixels: HashSet::from([(0, 0)]),
            value: 0,
        };

        let mut graph: UnGraph<MaorisNodeHash, ()> = UnGraph::new_undirected();

        let node_index1 = graph.add_node(node1);
        let node_index2 = graph.add_node(node2);
        let node_index3 = graph.add_node(node3);
        let node_index4 = graph.add_node(node4);
        let node_index5 = graph.add_node(node5);
        let node_index6 = graph.add_node(node6);

        graph.add_edge(node_index1, node_index2, ());
        graph.add_edge(node_index1, node_index6, ());

        graph.add_edge(node_index1, node_index3, ());
        graph.add_edge(node_index3, node_index2, ());

        graph.add_edge(node_index1, node_index4, ());
        graph.add_edge(node_index4, node_index2, ());

        graph.add_edge(node_index1, node_index5, ());
        graph.add_edge(node_index5, node_index2, ());

        let mut super_node = SuperMaorisNode::from(&node_index1, &graph);

        super_node.add(&node_index3, &graph);
        super_node.add(&node_index4, &graph);
        super_node.add(&node_index5, &graph);

        assert_eq!(super_node.neighbors.len(), 2);
        assert_eq!(super_node.nodes.len(), 4);
        assert!(super_node.neighbors.contains_key(&node_index2));
        assert!(super_node.nodes.contains(&node_index1));
        assert!(super_node.nodes.contains(&node_index3));
        assert!(super_node.nodes.contains(&node_index4));
        assert!(super_node.nodes.contains(&node_index5));
        assert_eq!(super_node.neighbors[&node_index2], 1);

        super_node.add(&node_index6, &graph);

        assert_eq!(super_node.neighbors.len(), 1);
        assert_eq!(super_node.nodes.len(), 5);
        assert!(super_node.neighbors.contains_key(&node_index2));
        assert!(super_node.nodes.contains(&node_index1));
        assert!(super_node.nodes.contains(&node_index3));
        assert!(super_node.nodes.contains(&node_index4));
        assert!(super_node.nodes.contains(&node_index5));
        assert!(super_node.nodes.contains(&node_index6));
        assert_eq!(super_node.neighbors[&node_index2], 1);
    }
}
