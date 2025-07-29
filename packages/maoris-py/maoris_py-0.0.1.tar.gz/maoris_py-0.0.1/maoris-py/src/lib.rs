use std::path::Path;

use pyo3::prelude::*;

use maoris_rs::fsi as fsi_rs;
use maoris_rs::maoris as maoris_rust;

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
#[pymodule]
fn maoris_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(distance_image, m)?)?;
    m.add_function(wrap_pyfunction!(fsi, m)?)?;
    m.add_function(wrap_pyfunction!(maoris, m)?)?;
    Ok(())
}

#[pyfunction]
fn distance_image(image_path: &str) -> PyResult<()> {
    let mut image = image::open(image_path).unwrap().into_luma8();
    let _ = fsi_rs::distance_image(&mut image);
    Ok(())
}

#[pyfunction]
fn fsi(image_path: &str, invert: bool) -> PyResult<()> {
    let mut image = image::open(image_path).unwrap().into_luma8();
    let _ = fsi_rs::fsi(&mut image, invert);
    Ok(())
}

#[pyfunction]
fn maoris(image_path: &str, output_folder: &str) -> PyResult<()> {
    let path = Path::new(image_path);
    let path_output = Path::new(output_folder);
    let _ = maoris_rust(path, path_output, false, false);
    Ok(())
}
