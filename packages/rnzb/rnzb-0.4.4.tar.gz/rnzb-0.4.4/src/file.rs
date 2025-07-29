use crate::segment::Segment;
use crate::tuple::Tuple;
use chrono::{DateTime, Utc};
use nzb_rs::{File as RustFile, Segment as RustSegment};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt::Debug;
use std::fmt::Display;

// Python wrapper class for File
#[pyclass(module = "rnzb", frozen, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct File {
    #[pyo3(get)]
    pub poster: String,
    #[pyo3(get)]
    pub posted_at: DateTime<Utc>,
    #[pyo3(get)]
    pub subject: String,
    #[pyo3(get)]
    pub groups: Tuple<String>,
    #[pyo3(get)]
    pub segments: Tuple<Segment>,
    #[serde(skip)]
    inner: RustFile,
}

// Implement Python-esque debug
impl Debug for File {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "File(poster={:?}, posted_at={:?}, subject={:?}, groups={:?}, segments={:?})",
            self.poster,
            self.posted_at.to_rfc3339(),
            self.subject,
            self.groups,
            self.segments
        )
    }
}

// Implement Python-esque display
// It's identical to Debug
impl Display for File {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self, f)
    }
}

// Implement conversion from RustFile to File
impl From<RustFile> for File {
    fn from(f: RustFile) -> Self {
        Self {
            poster: f.poster.clone(),
            posted_at: f.posted_at,
            subject: f.subject.clone(),
            groups: f.groups.clone().into(),
            segments: f
                .segments
                .clone()
                .into_iter()
                .map(Into::into)
                .collect::<Vec<_>>()
                .into(),
            inner: f,
        }
    }
}

// Implement conversion from File to RustFile
impl From<File> for RustFile {
    fn from(f: File) -> Self {
        RustFile::new(
            f.poster.clone(),
            f.posted_at,
            f.subject.clone(),
            f.groups.0.clone(),
            f.segments
                .0
                .into_iter()
                .map(Into::into)
                .collect::<Vec<RustSegment>>(),
        )
    }
}

#[pymethods]
impl File {
    #[new]
    #[pyo3(signature = (*, poster, posted_at, subject, groups, segments))]
    pub fn __new__(
        poster: String,
        posted_at: DateTime<Utc>,
        subject: String,
        groups: Vec<String>,
        segments: Vec<Segment>,
    ) -> Self {
        Self {
            poster: poster.clone(),
            posted_at,
            subject: subject.clone(),
            groups: groups.clone().into(),
            segments: segments.clone().into(),
            inner: RustFile::new(
                poster,
                posted_at,
                subject,
                groups,
                segments
                    .into_iter()
                    .map(Into::into)
                    .collect::<Vec<RustSegment>>(),
            ),
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

    // Size of the file calculated from the sum of segment sizes.
    #[getter]
    pub fn size(&self) -> u64 {
        self.inner.size()
    }

    // Complete name of the file with it's extension extracted from the subject.
    // May return [`None`] if it fails to extract the name.
    #[getter]
    pub fn name(&self) -> Option<&str> {
        self.inner.name()
    }

    // Base name of the file without it's extension extracted from the [`File::name`].
    // May return [`None`] if it fails to extract the stem.
    #[getter]
    pub fn stem(&self) -> Option<&str> {
        self.inner.stem()
    }

    //  Extension of the file extracted from the [`File::name`].
    //  May return [`None`] if it fails to extract the extension.
    #[getter]
    pub fn extension(&self) -> Option<&str> {
        self.inner.extension()
    }

    // Return [`true`] if the file has the specified extension, [`false`] otherwise.
    //
    // This method ensures consistent extension comparison
    // by normalizing the extension (removing any leading dot) and handling case-folding.
    #[pyo3(signature = (ext, /))]
    pub fn has_extension(&self, ext: &str) -> bool {
        self.inner.has_extension(ext)
    }

    // Return [`true`] if the file is a `.par2` file, [`false`] otherwise.
    pub fn is_par2(&self) -> bool {
        self.inner.is_par2()
    }

    // Return [`true`] if the file is a `.rar` file, [`false`] otherwise.
    pub fn is_rar(&self) -> bool {
        self.inner.is_rar()
    }

    // Return [`true`] if the file is obfuscated, [`false`] otherwise.
    pub fn is_obfuscated(&self) -> bool {
        self.inner.is_obfuscated()
    }
}
