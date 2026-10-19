# rpm-builder

A generic, lightweight RPM building repository. It automates the compilation, packaging, and publishing of test RPMs via GitHub Actions inside a CentOS 7 container.

## Background

During system-level testing, environment validation, or CI/CD pipeline debugging, there is often a need for "side-effect-free" RPM packages that only contain simple outputs. This project provides a standardized set of Go programs and `.spec` configurations, leveraging GitHub Actions to automatically generate such safe test RPMs. This avoids the risks associated with manually building RPMs in production environments.

## Directory Structure

```text
.
├── .github/workflows/build-rpm.yml   # CI/CD build and release workflow
├── cmd
│   ├── one/main.go                   # Test binary 1
│   ├── two/main.go                   # Test binary 2
│   └── three/main.go                 # Test binary 3
├── specs
│   ├── one.spec                      # RPM spec for 'one'
│   ├── two.spec                      # RPM spec for 'two'
│   └── three.spec                    # RPM spec for 'three'
└── go.mod                            # Go module definition
```

## Build Artifacts

Whenever a tag matching `v*` (e.g., `v0.0.1`) is pushed, GitHub Actions will automatically trigger the build and publish the following RPMs to the corresponding Release page:
- `one-1.0.0-1.el7.x86_64.rpm`
- `two-1.0.0-1.el7.x86_64.rpm`
- `three-1.0.0-1.el7.x86_64.rpm`

Upon installation, corresponding executables are generated in the system's `/usr/bin/` directory (which merely print test messages when executed).

## Technical Notes & Best Practices

Several typical issues encountered during the GitHub Actions build process have been resolved and standardized in this project:

1. **CentOS 7 EOL Source Failure**
   The official CentOS 7 repositories are offline. The workflow uses `sed` to replace the yum sources with the historical vault source `vault.centos.org` to ensure tools like `rpm-build` can be installed successfully.
2. **Avoiding YAML Heredoc Pitfalls**
   Dynamically generating `.spec` files via heredoc inside the workflow's `run:` block is strictly avoided (as it is highly prone to parsing crashes due to indentation). Instead, `.spec` files are stored as physical files in the `specs/` directory and directly copied (`cp`) into the container during the build.
3. **Architecture Standards (x86_64 vs noarch)**
   Since the compiled Go binaries are architecture-dependent ELF files, `BuildArch: x86_64` is uniformly declared in the `.spec` files, and the artifact collection path is explicitly set to `RPMS/x86_64/`. `noarch` should only be used if the package contains only script files.
4. **Release Publishing Permissions**
   Automatically uploading assets requires a Token with write permissions. It is necessary to configure an `ACCESS_TOKEN` in the repository's Secrets (Classic PATs require the `repo` scope, Fine-grained PATs require `Contents: write`), and to declare `permissions: contents: write` at the top level of the workflow as a fallback.

## Usage & Extension

1. **Trigger a Build**: Go to the `Actions` page in the repository and click `Run workflow` to trigger manually, or push a new tag directly (e.g., `git tag v0.0.2 && git push origin v0.0.2`).
2. **Download Artifacts**: Navigate to the Release page and download the corresponding `.rpm` files.
3. **Local Verification**:
   ```bash
   # Install
   yum install -y ./one-1.0.0-1.el7.x86_64.rpm
   
   # Verify
   rpm -qi one
   /usr/bin/one   # Expected output: Hello world from (1) one app
   ```

## How to Add a New Package?

1. Create a new target directory and a `main.go` under the `cmd/` directory.
2. Create a corresponding `.spec` file under the `specs/` directory, modifying the `Name`, `Source0` (corresponding to the binary name), and `%files` path.
3. Modify `.github/workflows/build-rpm.yml`:
    - Add `go build -o dist/bin/<new_name> ./cmd/<new_name>` to the compilation step.
    - Add `cp -v dist/bin/<new_name> ~/rpmbuild/SOURCES/<new_name>` to the container step.
    - Add `rpmbuild -ba ~/rpmbuild/SPECS/<new_name>.spec` to the build commands.
