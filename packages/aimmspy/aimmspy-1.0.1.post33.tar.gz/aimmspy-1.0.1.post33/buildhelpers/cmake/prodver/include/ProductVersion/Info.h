#pragma once


namespace ProductVersion{
	class Info{
	public:
		int getMajor() const;
		int getMinor() const;
		int getRelease() const;
		int getPatch() const;
		const char* getHash() const;
		const char* getBuildDate() const;
		const char* getBuildHost() const;
		const char* getArchitecture() const;
		const char* getBuildConfig() const;

        enum Platform{
            Platform_Windows,
            Platform_Linux
        };
        
        Platform getPlatform() const;

		static const Info& instance();
	private:
		Info();
	};
};

// end namespace ProductVersion
