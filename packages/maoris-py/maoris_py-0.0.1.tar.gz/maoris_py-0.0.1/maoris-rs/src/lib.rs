use image::{DynamicImage, GrayImage, ImageReader, Luma};
use std::path::Path;

mod maoris_lib;

pub use maoris_lib::fsi;
use maoris_lib::maoris;
pub use maoris_lib::watershed;

pub fn normalize(image: &mut GrayImage) -> () {
    let mut min = 255;
    let mut max = 0;
    for pixel in image.pixels() {
        if pixel[0] == 0 {
            continue;
        }
        if pixel[0] < min {
            min = pixel[0];
        }
        if pixel[0] > max {
            max = pixel[0];
        }
    }
    for pixel in image.pixels_mut() {
        if pixel[0] == 0 {
            continue;
        }
        let range = f32::from(max - min);
        pixel[0] = ((f32::from(pixel[0] - min)) / (range) * (255.0 - 50.0) + 50.0) as u8;
    }
}

/// Processes an image using the Maoris algorithm and saves the result to the specified output folder.
///
/// # Arguments
///
/// * `image_path` - A path to the input image file.
/// * `output_folder` - A path to the folder where the output image will be saved.
/// * `verbose` - A boolean flag indicating whether to print verbose output.
/// * `middle_outputs` - A boolean flag indicating whether to save intermediate outputs.
///
/// # Panics
///
/// The function will panic if the input image file does not exist or if there is an error decoding the image.
///
/// # Examples
///
/// ```
/// use std::path::Path;
/// use maoris_rs::maoris;
///
/// let image_path = Path::new("path/to/input/image.png");
/// let output_folder = Path::new("path/to/output/folder");
/// maoris(image_path, output_folder, true, true);
/// ```
pub fn maoris(image_path: &Path, output_folder: &Path, verbose: bool, middle_outputs: bool) -> () {
    if !image_path.exists() {
        println!("The file does not exist.");
        return;
    }

    let img: DynamicImage = match ImageReader::open(image_path) {
        Ok(reader) => match reader.decode() {
            Ok(img) => img,
            Err(e) => {
                panic!("Error: {}", e);
            }
        },
        Err(e) => {
            panic!("Error: {}", e);
        }
    };
    let luma: GrayImage = img.into_luma8();

    let mut luma_for_fsi = luma.clone();

    use std::time::Instant;
    let now = Instant::now();
    let mut fsi_image = match fsi::fsi(&mut luma_for_fsi, false) {
        Ok(image) => image,
        Err(e) => {
            println!("Error: {}", e);
            return;
        }
    };

    let elapsed = now.elapsed();
    if verbose {
        println!("FSI Elapsed: {:.2?}", elapsed);
    }

    normalize(&mut fsi_image);

    if middle_outputs {
        let filename = format!("outputs/fsi_image.png");
        fsi_image.save(filename).unwrap();
    }

    let (width, height) = fsi_image.dimensions();
    let mut discretized_fsi = GrayImage::new(width, height);

    // Iterate over the pixels and quantize their values to a multiple of x
    for (x, y, pixel) in fsi_image.enumerate_pixels() {
        let quantized_value = (f32::from(pixel[0]) / 10.0).round() * 10.0;
        let quantized_value = quantized_value as u8;
        discretized_fsi.put_pixel(x, y, Luma([quantized_value]));
    }

    if middle_outputs {
        let filename = format!("outputs/discretized_fsi.png");
        discretized_fsi.save(filename).unwrap();
    }

    let regions_graph = watershed::image_to_graph(&discretized_fsi);

    if verbose {
        let elapsed = now.elapsed();
        println!("Graph: {:.2?}", elapsed);
        println!("Initial number of regions {}", regions_graph.node_count());
        println!("Initial number of edges {}", regions_graph.edge_count());
    }

    let maoris = maoris::Maoris::from(regions_graph);

    if verbose {
        let elapsed = now.elapsed();
        println!("Elapsed: {:.2?}", elapsed);
        println!("Final number of regions {}", maoris.len());
    }

    let mut luma_final: GrayImage = GrayImage::new(luma.width(), luma.height());
    for region in maoris {
        region.draw(&mut luma_final);
    }

    //Normalize image between 0 and 255
    normalize(&mut luma_final);

    let save_path = format!("{}/maoris.png", output_folder.to_str().unwrap());

    luma_final.save(save_path).unwrap();
}
