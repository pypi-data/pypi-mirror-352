const RELEASES_API =
  'https://api.github.com/repos/shunirr/fontsplitta/releases/latest'

const FORMULA_TEMPLATE = `# typed: false
# frozen_string_literal: true

class Fontsplitta < Formula
  homepage "https://github.com/shunirr/fontsplitta"
  version "{{VERSION}}"
  depends_on :macos
  if Hardware::CPU.intel?
    url "{{X64_URL}}"
    def install
      bin.install "fontsplitta"
    end
  end
  if Hardware::CPU.arm?
    url "{{ARM64_URL}}"
    def install
      bin.install "fontsplitta"
    end
  end
end
`

async function writeNewFormula(args: {
  x64Link: string
  arm64Link: string
  version: string
}) {
  const formula = FORMULA_TEMPLATE.replaceAll('{{VERSION}}', args.version)
    .replaceAll('{{X64_URL}}', args.x64Link)
    .replaceAll('{{ARM64_URL}}', args.arm64Link)

  await Deno.writeTextFile('fontsplitta.rb', formula)
}

async function main() {
  const json = await (await fetch(RELEASES_API)).json()
  const newVersion = json.tag_name

  console.log('New version: ', newVersion)

  const x64 = json.assets.find((assets: { name: string }) =>
    assets.name.includes('darwin-x64')
  )
  const arm64 = json.assets.find((assets: { name: string }) =>
    assets.name.includes('darwin-arm64')
  )

  if (!x64 || !arm64) {
    throw new Error('Failed to extract x64 or arm64 download link')
  }

  const options = {
    x64Link: x64.browser_download_url,
    arm64Link: arm64.browser_download_url,
    version: newVersion,
  }
  console.log('Write new formula: ', options)
  await writeNewFormula(options)
  console.log('Complete write new formula')
}

main()
