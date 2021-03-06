<?php
/**
 * V6.php
 * 08-Nov-2011
 *
 * PHP Version 5
 *
 * @category Services
 * @package  Services_OpenStreetMap
 * @author   Ken Guest <kguest@php.net>
 * @license  BSD http://www.opensource.org/licenses/bsd-license.php
 * @version  Release: @package_version@
 * @link     V6.php
 */

/**
 * Services_OpenStreetMap_API_V06
 *
 * @category Services
 * @package  Services_OpenStreetMap
 * @author   Ken Guest <kguest@php.net>
 * @license  BSD http://www.opensource.org/licenses/bsd-license.php
 * @link     API_V06.php
 */
class Services_OpenStreetMap_API_V06
{
    /**
     * Elements supported by the API (v0.6).
     * Used for validation purposes.
     *
     * @var array
     *
     * @internal
     */
    protected $elements = ['changeset', 'node', 'relation', 'way'];

    /**
     * Transport
     *
     * @var Services_OpenStreetMap_Transport
     */
    protected $transport = null;

    /**
     * Config object, contains setting on how to interact with API Endpoint
     *
     * @var Services_OpenStreetMap_Config $config
     */
    protected $config = null;

    /**
     * Counter for assigning IDs to [newly] created objects.
     *
     * @var int
     *
     * @internal
     */
    protected $newId = -1;

    /**
     * Set Config object
     *
     * @param Services_OpenStreetMap_Config $config Config object.
     *
     * @return Services_OpenStreetMap_API_V06
     */
    public function setConfig(
        Services_OpenStreetMap_Config $config
    ): Services_OpenStreetMap_API_V06 {
        $this->config = $config;
        return $this;
    }

    /**
     * Get current Config object
     *
     * @return Services_OpenStreetMap_Config|null
     */
    public function getConfig():?Services_OpenStreetMap_Config
    {
        return $this->config;
    }

    /**
     * Set the Transport instance.
     *
     * @param Services_OpenStreetMap_Transport $transport Transport instance.
     *
     * @return Services_OpenStreetMap_API_V06
     */
    public function setTransport(
        Services_OpenStreetMap_Transport $transport
    ): Services_OpenStreetMap_API_V06 {
        $this->transport = $transport;
        return $this;
    }

    /**
     * Retrieve the current Transport instance.
     *
     * @return Services_OpenStreetMap_Transport.
     */
    public function getTransport(): Services_OpenStreetMap_Transport
    {
        return $this->transport;
    }

    /**
     * Get details of specified relation.
     *
     * Optionally specify which version of the relation to be retrieved.
     *
     * <code>
     * $r = $osm->getRelation(1234567);
     * $r = $osm->getRelation(1234567, 2);
     * </code>
     *
     * @param mixed $relationID ID of relation
     * @param mixed $version    [optional] version of relation
     *
     * @return Services_OpenStreetMap_Object
     * @throws Services_OpenStreetMap_Exception
     */
    public function getRelation(
        $relationID,
        $version = null
    ): Services_OpenStreetMap_Object {
        return $this->getTransport()->getObject('relation', $relationID, $version);
    }

    /**
     * Return an array of specified relations.
     *
     * Call with relation ids as parameters.
     *
     * <code>
     * $relations = $osm->getRelations($relationId, $relation2Id);
     * </code>
     *
     * @return Services_OpenStreetMap_Objects
     */
    public function getRelations(): Services_OpenStreetMap_Objects
    {
        return $this->getTransport()->getObjects(
            'relation',
            Services_OpenStreetMap::getIDs(func_get_args())
        );
    }

    /**
     * Get details of specified changeset.
     *
     * Optionally specify version of the changeset.
     *
     * <code>
     * $changeset = $osm->getChangeset(123456);
     * </code>
     *
     * @param string $id      numeric ID of changeset
     * @param string $version optional
     *
     * @return Services_OpenStreetMap_Object
     * @throws Services_OpenStreetMap_Exception
     */
    public function getChangeset(
        string $id,
        string $version = null
    ): Services_OpenStreetMap_Object {
        return $this->getTransport()->getObject('changeset', $id, $version);
    }

    /**
     * Create a changeset.
     *
     * Used to transmit changes (creation, updates, deletion)
     * to the server. Username and password must be set.
     *
     * <code>
     * $config = array('user' => 'fred@example.net', 'password' => 'wilma4eva');
     * $osm = new Services_OpenStreetMap($config);
     * $changeset = $osm->createChangeset(['reviewRequested' => true]);
     * </code>
     *
     * @param array $settings Changeset settings e.g. reviewRequested, message
     *
     * @return Services_OpenStreetMap_Changeset
     * @see    setConfig
     */
    public function createChangeset(
        array $settings = []
    ): Services_OpenStreetMap_Changeset {
        if (!array_key_exists('atomic', $settings)) {
            $settings['atomic'] = true;
        }
        if (!array_key_exists('reviewRequested', $settings)) {
            $settings['reviewRequested'] = false;
        }
        $changeset = new Services_OpenStreetMap_Changeset($settings);
        $changeset->setTransport($this->getTransport());
        $changeset->setConfig($this->getConfig());
        return $changeset;
    }

    /**
     * Search changesets for specified criteria.
     *
     * @param array $criteria Array of Services_OpenStreetMap_Criterion objects.
     *
     * @return Services_OpenStreetMap_Changesets|null|Services_OpenStreetMap_Objects
     * @throws Services_OpenStreetMap_RuntimeException
     */
    public function searchChangesets(array $criteria)
    : Services_OpenStreetMap_Changesets {
        $types = [];
        foreach ($criteria as $criterion) {
            $types[] = $criterion->type();
        }

        if (in_array('user', $types, true)
            && in_array('display_name', $types, true)
        ) {
            throw new Services_OpenStreetMap_RuntimeException(
                'Can\'t supply both user and display_name criteria'
            );
        }

        return $this->getTransport()->searchObjects('changeset', $criteria);
    }

    /**
     * Create and return a Services_OpenStreetMap_Node
     *
     * Latitude and longitude must be specified, array of tags optional.
     *
     * <code>
     * $node = $osm->createNode($lat, $lon, array('building' => 'yes'));
     * </code>
     *
     * @param float $latitude  Latitude of node
     * @param float $longitude Longitude of node
     * @param array $tags      Array of key->value tag pairs.
     *
     * @return Services_OpenStreetMap_Node
     */
    public function createNode(
        float $latitude,
        float $longitude,
        array $tags = []
    ): Services_OpenStreetMap_Node {
        $node = new Services_OpenStreetMap_Node();
        $config = $this->getConfig();
        $apiVersion = $config->getValue('api_version');
        $userAgent  = $config->getValue('User-Agent');
        foreach ($tags as $key => $value) {
            if (strlen($key) > 255 || strlen($value) > 255) {
                throw new Services_OpenStreetMap_RuntimeException(
                    "$key and its value are capped at 255 characters"
                );
            }
        }
        $xml = <<< XML
<?xml version='1.0' encoding='UTF-8'?>
<osm version='{$apiVersion}' generator='{$userAgent}'>
<node lat='{$latitude}' lon='{$longitude}' version='1'/></osm>
XML;
        $node->setLat($latitude);
        $node->setLon($longitude);
        $node->setXml(simplexml_load_string($xml));
        $node->setId((string) $this->newId--);
        if (!empty($tags)) {
            foreach ($tags as $key => $value) {
                $node->setTag($key, $value);
            }
        }
        return $node;
    }

    /**
     * Get a Services_OpenStreetMap_User object for the [current] user.
     *
     * May return false if the user could not be found for any reason.
     *
     * @see setConfig
     *
     * @return Services_OpenStreetMap_User|false
     * @throws Services_OpenStreetMap_Exception
     * @throws HTTP_Request2_Exception
     */
    public function getUser()
    {
        $response = null;
        $prefs = null;
        $config = $this->getConfig()->asArray();
        $url = $config['server']
            . 'api/'
            . $config['api_version']
            . '/user/details';
        $user = $config['user'];
        $password = $config['password'];
        try {
            $response = $this->getTransport()->getResponse(
                $url,
                HTTP_Request2::METHOD_GET,
                $user,
                $password
            );
        } catch (Services_OpenStreetMap_Exception $ex) {
            switch ($ex->getCode()) {
            case Services_OpenStreetMap_Transport::NOT_FOUND:
            case Services_OpenStreetMap_Transport::UNAUTHORISED:
            case Services_OpenStreetMap_Transport::GONE:
                return false;
            default:
                throw $ex;
            }
        }
        $url = $config['server'] . 'api/'
             . $config['api_version']
             . '/user/preferences';
        try {
            $prefs = $this->getTransport()->getResponse(
                $url,
                HTTP_Request2::METHOD_GET,
                $user,
                $password
            );
        } catch (Services_OpenStreetMap_Exception $ex) {
            switch ($ex->getCode()) {
            case Services_OpenStreetMap_Transport::NOT_FOUND:
            case Services_OpenStreetMap_Transport::UNAUTHORISED:
            case Services_OpenStreetMap_Transport::GONE:
                return false;
            default:
                throw $ex;
            }
        }
        $obj = new Services_OpenStreetMap_User();
        $obj->setXml(simplexml_load_string($response->getBody()));
        $obj->setPreferencesXml($prefs->getBody());
        $obj->setTransport($this->getTransport());
        $obj->setConfig($this->getConfig());
        return $obj;
    }

    /**
     * Get a Services_OpenStreetMap_User object for the specified user.
     *
     * May return false if the user could not be found for any reason.
     *
     * @param integer $id User Id.
     *
     * @see setConfig
     *
     * @return Services_OpenStreetMap_User|false
     * @throws Services_OpenStreetMap_Exception
     * @throws HTTP_Request2_Exception
     */
    public function getUserById(int $id)
    {
        $response = null;
        $config = $this->getConfig()->asArray();
        $url = $config['server']
            . 'api/'
            . $config['api_version']
            . '/user/' . $id;
        try {
            $response = $this->getTransport()->getResponse(
                $url,
                HTTP_Request2::METHOD_GET
            );
        } catch (Services_OpenStreetMap_Exception $ex) {
            switch ($ex->getCode()) {
            case Services_OpenStreetMap_Transport::NOT_FOUND:
            case Services_OpenStreetMap_Transport::UNAUTHORISED:
            case Services_OpenStreetMap_Transport::GONE:
                return false;
            default:
                throw $ex;
            }
        }
        $obj = new Services_OpenStreetMap_User();
        $obj->setXml(simplexml_load_string($response->getBody()));
        return $obj;
    }

    /**
     * Get details of specified way
     *
     * @param mixed $wayID   wayID
     * @param mixed $version [optional] version of way
     *
     * @return Services_OpenStreetMap_Object
     * @throws Services_OpenStreetMap_Exception
     */
    public function getWay($wayID, $version = null): Services_OpenStreetMap_Object
    {
        $way = $this->getTransport()->getObject('way', $wayID, $version);
        if ($way !== false) {
            $way->setTransport($this->getTransport());
            $way->setConfig($this->getConfig());
        }
        return $way;
    }

    /**
     * Get way plus full XML of all nodes referenced by it.
     *
     * API call retrieves a way or relation and all other elements referenced by it
     *
     * @param mixed $wayID   wayID
     * @param mixed $version Version of way
     *
     * @return Services_OpenStreetMap_Way
     * @note:  do a similary getRelationFull method also
     * @throws Services_OpenStreetMap_Exception
     */
    public function getWayFull($wayID, $version): Services_OpenStreetMap_Way
    {
        if (!is_numeric($version)) {
            throw new Services_OpenStreetMap_RuntimeException("Invalid version");
        }

        /** @var Services_OpenStreetMap_Way $way */
        $way = $this->getTransport()->getObject('way', $wayID, $version, 'full');
        if ($way !== false) {
            $way->setTransport($this->getTransport());
            $way->setConfig($this->getConfig());
        }
        return $way;
    }

    /**
     * Return an array of specified ways.
     *
     * Any number of ways can be specified.
     *
     * <code>
     * $ways = $osm->getWays($wayId, $way2Id);
     * </code>
     *
     * @return Services_OpenStreetMap_Ways|Services_OpenStreetMap_Objects
     */
    public function getWays(): Services_OpenStreetMap_Objects
    {
        return $this->getTransport()->getObjects(
            'way',
            Services_OpenStreetMap::getIDs(func_get_args())
        );
    }

    /**
     * Get details of specified node.
     *
     * Optionally, version of the node can be specified also.
     *
     * <code>
     * $osm = new Services_OpenStreetMap();
     * var_dump($osm->getNode(52245107));
     * </code>
     *
     * @param string $nodeID  nodeID
     * @param mixed  $version [optional] version of node
     *
     * @return Services_OpenStreetMap_Node|false
     * @throws Services_OpenStreetMap_Exception
     */
    public function getNode(string $nodeID, $version = null)
    {
        $node = $this->getTransport()->getObject('node', $nodeID, $version);
        if ($node !== null) {
            $node->setTransport($this->getTransport());
            $node->setConfig($this->getConfig());
        } else {
            $node = false;
        }
        return $node;
    }

    /**
     * Return an array of specified nodes.
     *
     * If none can be retrieved, for example if they all have been deleted,
     * then the boolean false value is returned.
     *
     * <code>
     * $osm = new Services_OpenStreetMap();
     * var_dump($osm->getNodes(52245107, 52245108));
     * </code>
     * Or
     * <code>
     * $osm = new Services_OpenStreetMap();
     * var_dump($osm->getNodes(array(52245107, 52245108)));
     * </code>
     *
     * @return Services_OpenStreetMap_Nodes|Services_OpenStreetMap_Objects
     */
    public function getNodes()
    {
        return $this->getTransport()->getObjects(
            'node',
            Services_OpenStreetMap::getIDs(func_get_args())
        );
    }

    /**
     * Retrieve bug data by bounding box.
     *
     * @param string  $minLon Min Longitude (leftmost point)
     * @param string  $minLat Min Latitude (bottom point)
     * @param string  $maxLon Max Longitude (rightmost point)
     * @param string  $maxLat Max Latitude (top point)
     * @param integer $limit  Number of entries to return at max, defaults to 100
     * @param integer $closed Number of days a bug needs to be closed to not be
     *                        included in the returned dataset. 0 means only open
     *                        bugs are returned, -1 means all are. Defaults to 7.
     *
     * @return Services_OpenStreetMap_Notes
     * @throws HTTP_Request2_Exception
     * @throws Services_OpenStreetMap_Exception
     */
    public function getNotesByBbox(
        string $minLon,
        string $minLat,
        string $maxLon,
        string $maxLat,
        int $limit = 100,
        int $closed = 7
    ): Services_OpenStreetMap_Notes {
        $config = $this->getConfig();
        $url = $config->getValue('server')
            . 'api/'
            . $config->getValue('api_version')
            . "/notes.xml?bbox=$minLon,$minLat,$maxLon,$maxLat"
            . "&limit=$limit&closed=$closed";
        $response = $this->getTransport()->getResponse($url);
        $collection = new Services_OpenStreetMap_Notes();
        $sxe = @simplexml_load_string($response->getBody());
        if ($config !== null) {
            $collection->setConfig($config);
        }
        $collection->setTransport($this->getTransport());
        $collection->setXml($sxe);
        return $collection;
    }

    /**
     * Retrieve bug data by search.
     *
     * @param string $searchTerm  Term(s) to search on
     * @param int    $limit       Number of entries to return at max, defaults to 100
     * @param int    $closed      Number of days a bug needs to be closed to not be
     *                            included in the returned dataset. 0 means only
     *                            open bugs are returned, -1 means all are.
     *                            Defaults to 7.
     * @param string $displayName Display-name of the creator of the returned notes.
     *                            Does not work together with the user parameter
     * @param int    $user        Valid user id
     * @param string $from        Start date in which to search notes within
     * @param string $to          End date in which to search notes within.
     *                            Defaults to current date
     *
     * @return Services_OpenStreetMap_Notes
     * @throws HTTP_Request2_Exception
     * @throws Services_OpenStreetMap_Exception
     */
    public function getNotesBySearch(
        string $searchTerm,
        int $limit = 100,
        int $closed = 7,
        string $displayName = '',
        int $user = 0,
        string $from = '',
        string $to = ''
    ): Services_OpenStreetMap_Notes {
        $config = $this->getConfig();
        $url = $config->getValue('server')
            . 'api/'
            . $config->getValue('api_version')
            . "/notes.xml'?q=$searchTerm";
        if ($displayName !== "") {
            $url .= "&display_name=$displayName";
        }
        if ($user !== 0 && $displayName === "") {
            $url .= "&user=$user";
        }
        if ($from !== "") {
            $url .= "&from=$from";
        }
        if ($to !== "") {
            $url .= "&to=$to";
        }
            $url .= "&limit=$limit&closed=$closed";
        $response = $this->getTransport()->getResponse($url);
        $collection = new Services_OpenStreetMap_Notes();
        $sxe = @simplexml_load_string($response->getBody());
        if ($config !== null) {
            $collection->setConfig($config);
        }
        $collection->setTransport($this);
        $collection->setXml($sxe);
        return $collection;
    }

    /**
     * Return array of granted permissions.
     *
     * The return array may be empty if authorisation failed.
     *
     * # allow_read_prefs (read user preferences)
     * # allow_write_prefs (modify user preferences)
     * # allow_write_diary (create diary entries, comments and make friends)
     * # allow_write_api (modify the map)
     * # allow_read_gpx (read private GPS traces)
     * # allow_write_gpx (upload GPS traces)
     *
     * @return array|false
     * @throws HTTP_Request2_Exception
     * @throws Services_OpenStreetMap_Exception
     */
    public function getPermissions()
    {
        $response = null;
        $config = $this->getConfig()->asArray();
        $user = $config['user'];
        $password = $config['password'];
        $url = $config['server']
            . 'api/'
            . $config['api_version']
            . '/permissions';
        try {
            $response = $this->getTransport()->getResponse(
                $url,
                HTTP_Request2::METHOD_GET,
                $user,
                $password
            );
        } catch (Services_OpenStreetMap_Exception $ex) {
            switch ($ex->getCode()) {
            case Services_OpenStreetMap_Transport::NOT_FOUND:
            case Services_OpenStreetMap_Transport::UNAUTHORISED:
            case Services_OpenStreetMap_Transport::GONE:
                return false;
            default:
                throw $ex;
            }
        }
        $obj = simplexml_load_string($response->getBody());
        $ret = [];
        $permissions = (array) $obj->permissions;
        if (isset($permissions['permission'])) {
            $permissions = $permissions['permission'];
            foreach ($permissions as $permission) {
                $ret[] = (string) $permission->attributes()->name;
            }
        }
        return $ret;
    }
}
