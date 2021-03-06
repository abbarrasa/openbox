#!/usr/bin/perl

# Copyright (C) 2015 Alberto Buitrago <echo YWJiYXJyYXNhQGdtYWlsLmNvbQo= | base64 -d>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# License: GPLv3
# Date: 16 June 2015
# Latest edit: 22 June 2015
# Website: https://github.com/abbarrasa/openbox
#
# A simple Perl script for Openbox which recent documents are displayed through pipe menus.
# It is based on obbrowser of Trizen. See <https://github.com/trizen/obbrowser>.

use XML::Parser;
use File::Basename;
use File::BaseDir qw(xdg_data_home xdg_config_home); # For Freedesktop.org base directory specification

my $pkgname = 'obrecent';
my $version = 0.1;

our $CONFIG;

my $home_dir =
	$ENV{HOME}
	|| $ENV{LOGDIR}
	|| (getpwuid($<))[7]
	|| `echo -n ~`;
my $config_documentation = <<"EOD";
#!/usr/bin/perl

# $pkgname - configuration file
# This file is updated automatically.
# Any additional comment and/or indentacion will be lost.

=for comment

|| ICON SETTINGS
	| icon_dirs_first   : When looking for icons, look in this directories first,
												before looking in the directories of the current icon theme.
			      						Example: [
                					"\$ENV{HOME}/My icons",
			      						],

	| icon_dirs_last    : Look in this directories at the very last, after looked in the
												directories of the current icon theme.
			      						Example: [
                        	"/usr/share/icons/Tango",
			      						],

	| with_icons	    	: A true value will make the script to use icons for files and dirs.
												This option may be slow, depending on your system configuration.

	| mime_ext_only	    : A true value will make the script to get the mimetype by extension only.
			      						This will improve the performance, since no content is read from files.

	| gtk_rc_filename   : Absolute path to your gtkrc file.
			      						This file is used to get the current icon theme name.
=cut

EOD

my %CONFIG = (
	'Linux::DesktopFiles' => {
		gtk_rc_filename  	=> "$home_dir/.gtkrc-2.0",
		skip_svg_icons	 	=> 0,
		icon_dirs_first  	=> undef,
		icon_dirs_second 	=> undef,
		icon_dirs_last	 	=> undef,
	},
	with_icons => 1,
);
my $xbel_file 	= xdg_data_home . "/recently-used.xbel";
my $config_dir  = xdg_config_home . "/obbrowser";
my $config_file = "$config_dir/config.pl";
my %table = (
	'&' => 'amp',
	'"' => 'quot',
	"'" => 'apos',
	'<' => 'lt',
	'>' => 'gt',
);
my $ld_obj;

# If exists, use obbrowser configuration
if (not -e $config_file or -z _) {
	# Create obrecent file configuration.
	# Create configuration directory if it's necessary
	$config_dir  = xdg_config_home . "/obrecent";
	$config_file = "$config_dir/config.pl";
	if (not -e $config_file or -z _) {
		if (not -d $config_dir) {
			require File::Path;
			File::Path::make_path($config_dir)
				or die "Can't create dir `$config_dir': $!";
		}
		dump_configuration();
	}
}


require $config_file; # Load the configuration file

my @valid_keys = grep exists $CONFIG{$_}, keys %{$CONFIG};
@CONFIG{@valid_keys} = @{$CONFIG}{@valid_keys};

if ($CONFIG{with_icons}) {
	use Linux::DesktopFiles;
	$Linux::DesktopFiles::VERSION >= 0.08
		|| die "Update Linux::DesktopFiles to a newer version! (requires >=0.08)\n";

	$ld_obj  = Linux::DesktopFiles->new(
				%{ $CONFIG{'Linux::DesktopFiles'} },
				home_dir	 => $home_dir,
				abs_icon_paths	 	=> 1,
				strict_icon_dirs 	=> 1,
				use_current_theme_icons => 1,
				icon_db_filename => "$config_dir/icons.db",
	);
}

my @bookmarks = ();
my $generated_menu = '';
if (-e $xbel_file) {
	my $parser = new XML::Parser(Handlers => {
			Start => \&handle_start
	});
	$parser->parsefile($xbel_file);
}

foreach my $bookmark (@bookmarks) {
	my $icon = '';
	if ($CONFIG{with_icons}) {
		use File::MimeInfo::Magic;
		my $mime_type = mimetype($bookmark) =~ tr{/}{-}r;
		$icon         = $ld_obj->get_icon_path($mime_type);
		if (not length($icon //= '')) {
			$icon = $ld_obj->get_icon_path('unknown');
		}
	}

	my $command = qq{xdg-open &quot;} . scape_quot($bookmark) . qq{&quot;};
	$generated_menu .= &print_entry(xml_escape(basename($bookmark)), $icon, $command);
}

$generated_menu .= qq{<separator/>}
			. &print_entry("Clear Recent Documents",
										($CONFIG{with_icons} ? $ld_obj->get_icon_path('edit-clear') : ''),
										qq{rm &quot;} . scape_quot($xbel_file) . qq{&quot;});
print "<openbox_pipe_menu>", $generated_menu, "</openbox_pipe_menu>";
exit;

# Subroutines
sub dump_configuration {
	use Data::Dumper;
	open my $config_fh, '>', $config_file
		or die "Can't open file '${config_file}' for write: $!";
	$Data::Dumper::Terse = 1;
	my $dumped_config = q{our $CONFIG = } . Dumper(\%CONFIG);
	print $config_fh $config_documentation, $dumped_config;
	close $config_fh;
}

sub handle_start {
	my ($p, $e, %a) = @_;
	if ($e eq 'bookmark') {
		if ($a{'href'}) {
			my $bookmark = $a{'href'};
			$bookmark =~ s/file:\/\///g;
			push @bookmarks, $bookmark
		}
	}
}

sub print_entry {
	qq{<item label="$_[0]"}
	. (length($_[1] //= '') ? qq{ icon="$_[1]"} : '')
	. qq{><action name="Execute"><command>$_[2]</command></action></item>};
}

sub xml_escape {
	# Convert hexadecimal into char code
	$_[0] =~ s/\%([a-fA-F0-9][a-fA-F0-9])/chr(hex($1))/eg;
	# Escape XML characters
	$_[0] =~ tr/&"'<>// ? $_[0] =~ s/([&"'<>])/&$table{$1};/gr : $_[0];
}

sub scape_quot {
	index($_[0], '&quot;') == -1 ? $_[0] : $_[0] =~ s/&quot;/\\&quot;/gr;
}
