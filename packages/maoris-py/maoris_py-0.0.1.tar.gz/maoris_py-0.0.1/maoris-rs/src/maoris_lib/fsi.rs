use image::{imageops::invert, GrayImage};
use image::{ImageBuffer, Luma};
use imageproc::distance_transform::{distance_transform, Norm};
use imageproc::drawing::draw_filled_circle_mut;
use rayon::iter::{IndexedParallelIterator, IntoParallelRefMutIterator, ParallelIterator};
use std::collections::HashMap;

struct PixelFSI {
    x: u32,
    y: u32,
    radius: u8,
}

pub fn distance_image(luma: &mut GrayImage) -> Result<GrayImage, image::ImageError> {
    //Threshold the distance image
    for pixel in luma.pixels_mut() {
        if pixel[0] > 100 {
            pixel[0] = 255;
        } else {
            pixel[0] = 0;
        }
    }

    let distance_image = distance_transform(&luma, Norm::L2);
    Ok(distance_image)
}

fn group_pixels(image: &GrayImage) -> HashMap<u8, Vec<PixelFSI>> {
    let pixels: Vec<PixelFSI> = image
        .enumerate_pixels()
        .map(|(x, y, pixel)| PixelFSI {
            x,
            y,
            radius: pixel[0],
        })
        .collect();

    let mut map = HashMap::new();

    // Group pixels by their value
    for pixel in pixels {
        map.entry(pixel.radius).or_insert_with(Vec::new).push(pixel);
    }

    map
}

/// Overlay an image at a given coordinate (x, y) but
/// ignores values of places that are not empty
fn overlay_fsi(
    bottom: &mut ImageBuffer<Luma<u8>, Vec<u8>>,
    top: &ImageBuffer<Luma<u8>, Vec<u8>>,
    original_image: &GrayImage,
) {
    let bottom_dims = bottom.dimensions();

    for y in 0..bottom_dims.1 {
        for x in 0..bottom_dims.0 {
            let p = top.get_pixel(x, y);
            let original_pixel = original_image.get_pixel(x, y);
            if original_pixel[0] == 255 || p[0] == 0 {
                continue;
            }
            let bottom_pixel = *p;
            bottom.put_pixel(x, y, bottom_pixel);
        }
    }
}

pub fn fsi(
    original_image: &mut GrayImage,
    invert_image: bool,
) -> Result<GrayImage, image::ImageError> {
    if invert_image {
        invert(original_image);
    }
    let distance_image_var = match distance_image(original_image) {
        Ok(distance_image_var) => distance_image_var,
        Err(e) => return Err(e),
    };

    // Group pixels by distance to be able to process them in parallel.
    let pixels_sort = group_pixels(&distance_image_var);

    let (width, height) = distance_image_var.dimensions();
    let mut fsi_images: Vec<GrayImage> = Vec::new();
    for _ in 0..pixels_sort.len() - 1 {
        let new_image: GrayImage = GrayImage::new(width, height);
        fsi_images.push(new_image);
    }

    // For each image we concurently draw the pixels of one radius.
    fsi_images
        .par_iter_mut()
        .enumerate()
        .for_each(|(index, image)| {
            // We skip the first image because it's empty
            if index == 0 {
                return;
            }
            let index_fsi = index - 1;
            let u8_index = index_fsi as u8;
            let pixels = pixels_sort.get(&u8_index).unwrap();

            pixels.iter().for_each(|pixel| {
                draw_filled_circle_mut(
                    image,
                    (pixel.x.try_into().unwrap(), pixel.y.try_into().unwrap()),
                    index_fsi as i32,
                    Luma([u8_index]),
                );
            });
        });

    // Then we merge all the images together, starting by the smallest radius.
    let mut canvas = ImageBuffer::new(width, height);
    for index in 0..fsi_images.len() {
        overlay_fsi(&mut canvas, &fsi_images[index], &original_image);
    }

    Ok(canvas)
}

// Unit tests
#[cfg(test)]
mod test {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_fsi() {
        // a default (black) image
        let mut test_image: GrayImage = GrayImage::new(3, 3);
        // set a central pixel to white
        test_image.get_pixel_mut(0, 0).0 = [255];
        let distance_image = match distance_image(&mut test_image) {
            Ok(image) => image,
            Err(_) => panic!("Error in distance_image"),
        };

        let mut distance_image_correct: GrayImage = GrayImage::new(3, 3);
        distance_image_correct.get_pixel_mut(1, 0).0 = [1];
        distance_image_correct.get_pixel_mut(2, 0).0 = [2];
        distance_image_correct.get_pixel_mut(0, 1).0 = [1];
        distance_image_correct.get_pixel_mut(0, 2).0 = [2];
        distance_image_correct.get_pixel_mut(1, 1).0 = [2];
        distance_image_correct.get_pixel_mut(2, 2).0 = [3];
        distance_image_correct.get_pixel_mut(1, 2).0 = [3];
        distance_image_correct.get_pixel_mut(2, 1).0 = [3];
        assert_eq!(distance_image, distance_image_correct);
    }
}
