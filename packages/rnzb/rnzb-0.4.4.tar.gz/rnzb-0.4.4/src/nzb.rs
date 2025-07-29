use crate::exception::InvalidNzbError;
use crate::file::File;
use crate::meta::Meta;
use crate::tuple::Tuple;
use nzb_rs::Nzb as RustNzb;
use pyo3::exceptions::PyFileNotFoundError;
use pyo3::prelude::*;
use pyo3::types::PyType;
use serde::{Deserialize, Serialize};
use std::fmt::Debug;
use std::fmt::Display;
use std::io;
use std::path::PathBuf;

// Python wrapper class for NZB
#[pyclass(module = "rnzb", frozen, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Nzb {
    #[pyo3(get)]
    pub meta: Meta,
    #[pyo3(get)]
    pub files: Tuple<File>,
    #[serde(skip)]
    inner: RustNzb,
}

// Implement Python-esque debug
impl Debug for Nzb {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Nzb(meta={:?}, files={:?})", self.meta, self.files)
    }
}

// Implement Python-esque display
// It's identical to Debug
impl Display for Nzb {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self, f)
    }
}

// Implement conversion from RustNzb to Nzb
impl From<RustNzb> for Nzb {
    fn from(n: RustNzb) -> Self {
        Self {
            meta: Meta::from(n.meta.clone()),
            files: n
                .files
                .clone()
                .into_iter()
                .map(Into::into)
                .collect::<Vec<_>>()
                .into(),
            inner: n,
        }
    }
}

#[pymethods]
impl Nzb {
    #[new]
    #[pyo3(signature = (*, meta, files))]
    pub fn __new__(meta: Meta, files: Vec<File>) -> Self {
        Self {
            meta: meta.clone(),
            files: files.clone().into(),
            inner: RustNzb {
                meta: meta.into(),
                files: files.into_iter().map(Into::into).collect::<Vec<_>>(),
            },
        }
    }

    pub fn __repr__(&self) -> String {
        format!("{:?}", self)
    }

    pub fn __str__(&self) -> String {
        self.__repr__()
    }

    pub fn __copy__(&self) -> Self {
        self.clone()
    }

    #[classmethod]
    #[pyo3(signature = (nzb, /))]
    #[allow(unused_variables)]
    pub fn from_str(cls: &Bound<'_, PyType>, nzb: &str) -> PyResult<Nzb> {
        match RustNzb::parse(nzb) {
            Ok(nzb) => Ok(Nzb::from(nzb)),
            Err(e) => Err(InvalidNzbError::new_err(e.to_string())),
        }
    }

    #[classmethod]
    #[pyo3(signature = (nzb, /))]
    #[allow(unused_variables)]
    pub fn from_file(cls: &Bound<'_, PyType>, nzb: PathBuf) -> PyResult<Nzb> {
        match RustNzb::parse_file(nzb) {
            Ok(nzb) => Ok(Nzb::from(nzb)),
            Err(err) => match err {
                nzb_rs::ParseNzbFileError::Io { source, file }
                    if source.kind() == io::ErrorKind::NotFound =>
                {
                    Err(PyFileNotFoundError::new_err(file))
                }
                _ => Err(InvalidNzbError::new_err(err.to_string())),
            },
        }
    }

    #[classmethod]
    #[allow(unused_variables)]
    #[pyo3(signature = (json, /))]
    pub fn from_json(cls: &Bound<'_, PyType>, json: &str) -> PyResult<Nzb> {
        let nzb: RustNzb =
            serde_json::from_str(json).map_err(|e| InvalidNzbError::new_err(e.to_string()))?;
        Ok(Nzb::from(nzb))
    }

    #[pyo3(signature = (*, pretty=false))]
    pub fn to_json(&self, pretty: bool) -> PyResult<String> {
        if pretty {
            serde_json::to_string_pretty(&self).map_err(|e| InvalidNzbError::new_err(e.to_string()))
        } else {
            serde_json::to_string(&self).map_err(|e| InvalidNzbError::new_err(e.to_string()))
        }
    }

    #[getter]
    pub fn file(&self) -> File {
        // self.files is guranteed to have atleast one file, so we can safely unwrap().
        File::from(self.inner.file().clone())
    }

    // Total size of all the files in the NZB.
    #[getter]
    pub fn size(&self) -> u64 {
        self.inner.size()
    }

    // Vector of unique file names across all the files in the NZB.
    #[getter]
    pub fn filenames(&self) -> Tuple<&str> {
        self.inner.filenames().into()
    }

    // Vector of unique posters across all the files in the NZB.
    #[getter]
    pub fn posters(&self) -> Tuple<&str> {
        self.inner.posters().into()
    }

    // Vector of unique groups across all the files in the NZB.
    #[getter]
    pub fn groups(&self) -> Tuple<&str> {
        self.inner.groups().into()
    }

    // Vector of .par2 files in the NZB.
    #[getter]
    pub fn par2_files(&self) -> Tuple<File> {
        self.inner
            .par2_files()
            .into_iter()
            .map(|f| f.clone().into())
            .collect::<Vec<File>>()
            .into()
    }

    // Total size of all the `.par2` files.
    #[getter]
    pub fn par2_size(&self) -> u64 {
        self.inner.par2_size()
    }

    // Percentage of the size of all the `.par2` files relative to the total size.
    #[getter]
    pub fn par2_percentage(&self) -> f64 {
        self.inner.par2_percentage()
    }

    // Return [`true`] if the file has the specified extension, [`false`] otherwise.
    //
    // This method ensures consistent extension comparison
    // by normalizing the extension (removing any leading dot) and handling case-folding.
    #[pyo3(signature = (ext, /))]
    pub fn has_extension(&self, ext: &str) -> bool {
        self.inner.has_extension(ext)
    }

    // Return [`true`] if there's at least one `.par2` file in the NZB, [`false`] otherwise.
    pub fn has_par2(&self) -> bool {
        self.inner.has_par2()
    }

    // Return [`true`] if any file in the NZB is a `.rar` file, [`false`] otherwise.
    pub fn has_rar(&self) -> bool {
        self.inner.has_rar()
    }

    // Return [`true`] if every file in the NZB is a `.rar` file, [`false`] otherwise.
    pub fn is_rar(&self) -> bool {
        self.inner.is_rar()
    }

    // Return [`true`] if any file in the NZB is obfuscated, [`false`] otherwise.
    pub fn is_obfuscated(&self) -> bool {
        self.inner.is_obfuscated()
    }
}
