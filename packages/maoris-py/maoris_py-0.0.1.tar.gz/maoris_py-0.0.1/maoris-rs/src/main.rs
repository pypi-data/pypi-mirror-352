use clap::Parser;
use maoris_rs::maoris;
use std::path::Path;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[arg(short, long)]
    image_path: String,

    #[arg(short, long)]
    output_path: String,

    #[arg(short, long)]
    verbose: bool,

    #[arg(short, long)]
    middle_outputs: bool,
}

fn main() {
    let args = Args::parse();

    let image_path = Path::new(&args.image_path);
    let output_path = Path::new(&args.output_path);
    maoris(image_path, output_path, args.verbose, args.middle_outputs);
}
